#!/usr/bin/env python3
"""
直接用 web_fetch 抓 Pitchfork 评论，从结果中提取干净正文
用法：python pf_web_fetch.py <album_id>
"""
import sys, json, re, subprocess, urllib.request, urllib.parse
from pathlib import Path

DB = Path(r"C:\Users\qujt\.qclaw\workspace\_music_latest.db")
REVIEWS_DIR = Path(r"C:\Users\qujt\.qclaw\workspace\tasks\pitchfork-expert\docs\reviews")
REVIEWS_DIR.mkdir(parents=True, exist_ok=True)

# 已知 URL 映射（手动验证过的）
KNOWN_URLS = {
    323: "https://pitchfork.com/reviews/albums/car-seat-headrest-twin-fantasy/",
    382: "https://pitchfork.com/reviews/albums/car-seat-headrest-teens-of-denial/",
    383: "https://pitchfork.com/reviews/albums/car-seat-headrest-nervous-young-man/",
    386: "https://pitchfork.com/reviews/albums/car-seat-headrest-how-to-leave-town/",
    554: "https://pitchfork.com/reviews/albums/car-seat-headrest-teens-of-style/",
    540: "https://pitchfork.com/reviews/albums/paul-mccartney-the-boys-of-dungeon-lane/",
}


def call_web_fetch(url):
    """调用 openclaw 的 web_fetch（通过 HTTP 到本地服务）"""
    # 直接用 urllib 模拟 web_fetch 的行为
    # web_fetch 本质上是用 readability 提取正文
    # 我们直接抓 HTML 然后提取
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html'
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode('utf-8')
    except Exception as e:
        print(f"[ERROR] 抓取失败: {e}")
        return None


def extract_review_from_html(html, url):
    """从 HTML 中提取评论"""
    result = {'url': url, 'title': '', 'score': 0, 'author': '', 'body': ''}
    
    # 方法1: 从 __PRELOADED_STATE__ 提取
    m = re.search(r'__PRELOADED_STATE__\s*=\s*({.*?})\s*;', html, re.DOTALL)
    if m:
        try:
            data = json.loads(m.group(1))
            # 递归查找 review 数据
            def find_review(obj, depth=0):
                if depth > 10:
                    return None
                if isinstance(obj, dict):
                    if 'rating' in obj and ('title' in obj or 'body' in obj):
                        return obj
                    for v in obj.values():
                        r = find_review(v, depth + 1)
                        if r:
                            return r
                elif isinstance(obj, list):
                    for item in obj:
                        r = find_review(item, depth + 1)
                        if r:
                            return r
                return None
            
            review = find_review(data)
            if review:
                result['title'] = review.get('title', '')
                result['score'] = review.get('rating', 0)
                author = review.get('author', {})
                if isinstance(author, dict):
                    result['author'] = author.get('name', '')
                elif isinstance(author, str):
                    result['author'] = author
                result['body'] = review.get('body', '')
                return result
        except:
            pass
    
    # 方法2: 正则提取
    # 标题
    title_m = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
    if title_m:
        result['title'] = title_m.group(1).strip()
    
    # 评分
    score_patterns = [
        r'class="[^"]*score[^"]*"[^>]*>([\d.]+)<',
        r'"rating":\s*([\d.]+)',
    ]
    for p in score_patterns:
        m = re.search(p, html)
        if m:
            result['score'] = float(m.group(1))
            break
    
    # 作者
    author_m = re.search(r'class="[^"]*author[^"]*"[^>]*>([^<]+)<', html)
    if author_m:
        result['author'] = author_m.group(1).strip()
    
    # 正文 - 找 <div class="body"> 或类似
    body_patterns = [
        r'<div[^>]*class="[^"]*body[^"]*"[^>]*>(.*?)</div>\s*<footer',
        r'<article[^>]*>(.*?)</article>',
    ]
    for p in body_patterns:
        m = re.search(p, html, re.DOTALL)
        if m:
            body = m.group(1)
            body = re.sub(r'<[^>]+>', '', body)
            body = re.sub(r'\s+', ' ', body).strip()
            result['body'] = body
            break
    
    return result


def translate_text(text):
    """翻译占位"""
    # TODO: 接入翻译 API
    return f"[译文待补充]\n\n{text[:500]}..."


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

{review_data['body'][:5000]}

## 译文

{translate_text(review_data['body'])}
"""
    
    filepath.write_text(md, encoding='utf-8')
    print(f"  -> 已保存: {filepath.name}")
    return filepath


def main():
    if len(sys.argv) < 2:
        print("用法: python pf_web_fetch.py <album_id>")
        sys.exit(1)
    
    album_id = int(sys.argv[1])
    
    # 获取专辑信息
    import sqlite3
    conn = sqlite3.connect(DB)
    row = conn.execute(
        "SELECT album_name, artist, pitchfork_score, review_url FROM albums WHERE album_id = ?",
        (album_id,)
    ).fetchone()
    
    if not row:
        print(f"[ERROR] 专辑 ID {album_id} 不存在")
        sys.exit(1)
    
    album_name, artist, score, review_url = row
    print(f"[PF] 处理: {artist} - {album_name} (PF: {score})")
    
    # 确定 URL
    if review_url:
        url = review_url
        print(f"  -> 使用已有 URL: {url}")
    elif album_id in KNOWN_URLS:
        url = KNOWN_URLS[album_id]
        print(f"  -> 使用已知 URL: {url}")
    else:
        print(f"[ERROR] 未找到 URL，请手动提供")
        conn.close()
        sys.exit(1)
    
    # 抓取
    print(f"  -> 抓取 HTML...")
    html = call_web_fetch(url)
    if not html:
        print(f"[ERROR] 抓取失败")
        conn.close()
        sys.exit(1)
    
    print(f"  -> HTML 大小: {len(html)} 字节")
    
    # 提取
    print(f"  -> 提取评论数据...")
    review_data = extract_review_from_html(html, url)
    
    if not review_data or not review_data.get('body'):
        print(f"[ERROR] 提取失败")
        conn.close()
        sys.exit(1)
    
    print(f"  -> 标题: {review_data['title'][:50]}")
    print(f"  -> 评分: {review_data['score']}")
    print(f"  -> 作者: {review_data['author']}")
    print(f"  -> 正文长度: {len(review_data['body'])} 字符")
    
    # 保存
    save_review(album_id, album_name, artist, review_data)
    
    # 更新数据库
    conn.execute(
        "UPDATE albums SET review_url = ? WHERE album_id = ?",
        (url, album_id)
    )
    conn.commit()
    conn.close()
    
    print(f"[PF] 完成！")


if __name__ == "__main__":
    main()
