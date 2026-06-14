#!/usr/bin/env python3
"""
Pitchfork 评论抓取 v3 —— 用 web_fetch 拿 markdown，然后精准提取
用法：python pf_review_v3.py <album_id>
"""
import sys, json, re, time, urllib.request, subprocess
from pathlib import Path

DB = Path(r"C:\Users\qujt\.qclaw\workspace\_music_latest.db")
REVIEWS_DIR = Path(r"C:\Users\qujt\.qclaw\workspace\tasks\pitchfork-expert\docs\reviews")
REVIEWS_DIR.mkdir(parents=True, exist_ok=True)

# Pitchfork 评论 URL 格式（已验证）：/reviews/albums/{artist}-{album}/
# 注意：实际 URL 需要查，不能靠猜测
# 这里用 web_search 先找 URL，再用 web_fetch 抓内容

def get_review_url_via_search(album_name, artist):
    """用搜索引擎找 Pitchfork 评论 URL"""
    # 简化：直接用已知的 URL 格式试
    # 实际应该搜索，这里先硬编码几个已知的
    known = {
        "Twin Fantasy": "https://pitchfork.com/reviews/albums/car-seat-headrest-twin-fantasy/",
        "Teens of Denial": "https://pitchfork.com/reviews/albums/car-seat-headrest-teens-of-denial/",
        "Train on the Island": "https://pitchfork.com/reviews/albums/aldous-harding-train-on-the-island/",
        "Beauty Land": "https://pitchfork.com/reviews/albums/greg-mendez-beauty-land/",
        "Bitknot": "https://pitchfork.com/reviews/albums/feeble-little-horse-bitknot/",
    }
    for key, url in known.items():
        if key.lower() in album_name.lower() or key.lower() in artist.lower():
            return url
    return None

def fetch_via_python(album_id):
    """用 Python urllib 直接抓，避免 PowerShell 转义问题"""
    import sqlite3
    conn = sqlite3.connect(DB)
    row = conn.execute(
        "SELECT album_name, artist, pitchfork_score, review_url FROM albums WHERE album_id = ?",
        (album_id,)
    ).fetchone()
    conn.close()
    
    if not row:
        print(f"[ERROR] 专辑 ID {album_id} 不存在")
        return None
    
    album_name, artist, score, review_url = row
    print(f"[PF] 处理: {artist} - {album_name} (PF: {score})")
    
    if not review_url:
        review_url = get_review_url_via_search(album_name, artist)
        if not review_url:
            print(f"[ERROR] 找不到 review URL，请手动提供")
            return None
        print(f"  -> 使用 URL: {review_url}")
    
    # 用 urllib 抓 HTML
    print(f"  -> 抓取 HTML...")
    try:
        req = urllib.request.Request(review_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8')
        print(f"  -> HTML 大小: {len(html)} 字节")
    except Exception as e:
        print(f"  -> 抓取失败: {e}")
        return None
    
    # 从 HTML 手动提取（简单的正则，针对 Pitchfork 的实际结构）
    # 提取标题
    title_m = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
    title = title_m.group(1).strip() if title_m else album_name
    
    # 提取评分（Pitchfork 的评分通常在 class 包含 "score" 的元素中）
    score_m = re.search(r'class="[^"]*score[^"]*"[^>]*>([\d.]+)<', html)
    # 如果上面没找到，尝试从 __PRELOADED_STATE__ 里找
    if not score_m:
        m = re.search(r'__PRELOADED_STATE__\s*=\s*({.*?})\s*;', html, re.DOTALL)
        if m:
            try:
                data = json.loads(m.group(1))
                # 简单的递归查找
                def find_rating(obj):
                    if isinstance(obj, dict):
                        if 'rating' in obj:
                            return obj['rating']
                        for v in obj.values():
                            r = find_rating(v)
                            if r:
                                return r
                    elif isinstance(obj, list):
                        for item in obj:
                            r = find_rating(item)
                            if r:
                                return r
                    return None
                rating = find_rating(data)
                if rating:
                    score = float(rating)
            except:
                pass
    
    # 提取作者
    author_m = re.search(r'class="[^"]*author[^"]*"[^>]*>([^<]+)<', html)
    if not author_m:
        # 从 byline 里找
        author_m = re.search(r'[Bb]y\s+([A-Za-z\s.]+?)\s*(?:Reviewed|·|$)', html)
    author = author_m.group(1).strip() if author_m else ""
    
    # 提取正文 —— 直接找 <div class="body"> 或类似容器
    body = ""
    # 方案1: 找 <div class="body">
    body_m = re.search(r'<div[^>]*class="[^"]*body[^"]*"[^>]*>(.*?)</div>\s*<footer', html, re.DOTALL)
    if body_m:
        body = body_m.group(1)
    else:
        # 方案2: 找 <article>
        body_m = re.search(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)
        if body_m:
            body = body_m.group(1)
    
    if body:
        # 去掉所有 HTML 标签
        body = re.sub(r'<[^>]+>', '', body)
        # 去掉多余空白
        body = re.sub(r'\s+', ' ', body).strip()
        # 去掉开头的垃圾（比如 "0.0Albums..." 等）
        # 找到第一个有意义的句子（以大写字母开头，有一定长度）
        sentences = re.split(r'(?<=[.!?])\s+', body)
        clean_sentences = []
        for s in sentences:
            s = s.strip()
            if len(s) > 30 and re.match(r'^[A-Z]', s):
                clean_sentences.append(s)
        if clean_sentences:
            body = ' '.join(clean_sentences)
    
    result = {
        'title': title,
        'score': score if isinstance(score, (int, float)) else 0,
        'author': author,
        'url': review_url,
        'body': body[:5000]  # 限制长度
    }
    
    # 保存
    save_review(album_id, album_name, artist, result)
    
    # 更新数据库
    conn = sqlite3.connect(DB)
    conn.execute(
        "UPDATE albums SET review_url = ? WHERE album_id = ?",
        (review_url, album_id)
    )
    conn.commit()
    conn.close()
    
    print(f"[PF] 完成！")
    return result

def save_review(album_id, album_name, artist, review_data):
    """保存为 Markdown"""
    filename = f"{album_id}_{artist.replace(' ', '_')}_{album_name.replace(' ', '_')[:20]}.md"
    filepath = REVIEWS_DIR / filename
    
    md = f"""# {review_data['title']}

> 艺人：{artist}
> 专辑：{album_name}
> 评分：{review_data['score']}
> 作者：{review_data['author']}
> 原文：{review_data['url']}

## 原文

{review_data['body'][:3000]}

## 译文

[译文待补充]
"""
    
    filepath.write_text(md, encoding='utf-8')
    print(f"  -> 已保存: {filepath.name}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python pf_review_v3.py <album_id>")
        sys.exit(1)
    
    album_id = int(sys.argv[1])
    fetch_via_python(album_id)
