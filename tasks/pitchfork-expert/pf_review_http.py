#!/usr/bin/env python3
"""Pitchfork 评论抓取 + 翻译（HTTP 版）"""
import sys, json, re, time
import urllib.request
from pathlib import Path

DB = Path(r"C:\Users\qujt\.qclaw\workspace\_music_latest.db")
REVIEWS_DIR = Path(r"C:\Users\qujt\.qclaw\workspace\tasks\pitchfork-expert\docs\reviews")
REVIEWS_DIR.mkdir(parents=True, exist_ok=True)


def get_album_info(album_id):
    """从数据库获取专辑信息"""
    import sqlite3
    conn = sqlite3.connect(DB)
    row = conn.execute(
        "SELECT album_name, artist, pitchfork_score, review_url FROM albums WHERE album_id = ?",
        (album_id,)
    ).fetchone()
    conn.close()
    return row


def fetch_pf_review_http(album_name, artist):
    """用 HTTP 抓取 Pitchfork 评论"""
    # 1. 搜索 Pitchfork 评论 URL
    query = f"{artist} {album_name}".replace(" ", "-").lower()
    search_url = f"https://pitchfork.com/search/?query={query}"
    
    try:
        # 尝试直接构造 URL（Pitchfork URL 格式：/reviews/albums/xxx-artist-album/）
        album_slug = f"{artist.lower().replace(' ', '-')}-{album_name.lower().replace(' ', '-')}"
        review_url = f"https://pitchfork.com/reviews/albums/{album_slug}/"
        
        print(f"  -> 尝试 URL: {review_url}")
        
        req = urllib.request.Request(review_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8')
        
        # 提取 __PRELOADED_STATE__
        m = re.search(r'__PRELOADED_STATE__\s*=\s*({.*?});', html, re.DOTALL)
        if m:
            data = json.loads(m.group(1))
            return parse_pf_data(data, html, review_url)
        
        # 如果没找到，尝试提取静态内容
        return parse_html_static(html, review_url)
        
    except Exception as e:
        print(f"  -> HTTP 失败: {e}")
        return None


def parse_pf_data(data, html, url):
    """解析 __PRELOADED_STATE__ 数据"""
    try:
        # 导航到评论数据
        review = data.get('review', {})
        
        title = review.get('title', '')
        score = review.get('rating', 0)
        author = review.get('author', {}).get('name', '')
        body = review.get('body', '')
        
        if not body:
            # 尝试从 HTML 提取
            body = extract_body_from_html(html)
        
        return {
            'title': title,
            'score': score,
            'author': author,
            'url': url,
            'body': body
        }
    except Exception as e:
        print(f"  -> 解析失败: {e}")
        return None


def extract_body_from_html(html):
    """从 HTML 提取正文（正则）"""
    # 尝试多种模式
    patterns = [
        r'<div[^>]*class="[^"]*body[^"]*"[^>]*>(.*?)</div>\s*<footer',
        r'<article[^>]*>(.*?)</article>',
        r'class="contents">(.*?)</div>',
    ]
    
    for p in patterns:
        m = re.search(p, html, re.DOTALL)
        if m:
            body = m.group(1)
            body = re.sub(r'<[^>]+>', '', body)
            body = re.sub(r'\s+', ' ', body).strip()
            return body
    
    return ""


def parse_html_static(html, url):
    """解析静态 HTML"""
    # 提取标题
    title_m = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
    title = title_m.group(1).strip() if title_m else ""
    
    # 提取评分
    score_m = re.search(r'class="[^"]*score[^"]*"[^>]*>([\d.]+)</', html)
    score = float(score_m.group(1)) if score_m else 0
    
    # 提取作者
    author_m = re.search(r'class="[^"]*author[^"]*"[^>]*>([^<]+)</', html)
    author = author_m.group(1).strip() if author_m else ""
    
    # 提取正文
    body = extract_body_from_html(html)
    
    return {
        'title': title,
        'score': score,
        'author': author,
        'url': url,
        'body': body
    }


def translate_text(text):
    """翻译（占位，实际应调用翻译 API）"""
    # TODO: 接入翻译 API
    return f"[译文待补充]\n\n{text[:500]}..."


def save_review(album_id, album_name, artist, review_data):
    """保存评论为 Markdown"""
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

{translate_text(review_data['body'])}
"""
    
    filepath.write_text(md, encoding='utf-8')
    print(f"  -> 已保存: {filepath.name}")
    return filepath


def main():
    if len(sys.argv) < 2:
        print("用法: python pf_review_http.py <album_id>")
        sys.exit(1)
    
    album_id = int(sys.argv[1])
    
    # 获取专辑信息
    row = get_album_info(album_id)
    if not row:
        print(f"[ERROR] 专辑 ID {album_id} 不存在")
        sys.exit(1)
    
    album_name, artist, score, review_url = row
    print(f"[PF] 处理: {artist} - {album_name} (PF: {score})")
    
    # 如果已有 review_url，直接抓取
    if review_url:
        print(f"  -> 使用已有 URL: {review_url}")
        review_data = fetch_pf_review_http(album_name, artist)
    else:
        review_data = fetch_pf_review_http(album_name, artist)
    
    if not review_data:
        print(f"[ERROR] 抓取失败")
        sys.exit(1)
    
    # 保存
    save_review(album_id, album_name, artist, review_data)
    
    # 更新数据库
    import sqlite3
    conn = sqlite3.connect(DB)
    conn.execute(
        "UPDATE albums SET review_url = ? WHERE album_id = ?",
        (review_data['url'], album_id)
    )
    conn.commit()
    conn.close()
    
    print(f"[PF] 完成！")


if __name__ == "__main__":
    main()
