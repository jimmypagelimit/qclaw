#!/usr/bin/env python3
"""
Pitchfork 评论抓取 + 翻译
用法: python pf_review_scraper.py <album_id>
"""
import sys, time, re, json
import cloakbrowser
from pathlib import Path

DB = Path(r"C:\Users\qujt\.qclaw\workspace\_music_latest.db")
REVIEWS_DIR = Path(r"C:\Users\qujt\.qclaw\workspace\tasks\pitchfork-expert\docs\reviews")
REVIEWS_DIR.mkdir(parents=True, exist_ok=True)


def get_review_url(album_id):
    """从数据库获取 review_url"""
    import sqlite3
    conn = sqlite3.connect(DB)
    row = conn.execute("SELECT review_url FROM albums WHERE album_id = ?", (album_id,)).fetchone()
    conn.close()
    return row[0] if row and row[0] else None


def search_pf_review(page, album_name, artist):
    """搜索 PF 评论 URL"""
    query = f"{artist} {album_name} site:pitchfork.com"
    page.evaluate(f'location.href = "https://www.google.com/search?q={query.replace(" ", "+")}"')
    time.sleep(5)
    
    # 提取第一个 pitchfork.com 链接
    html = page.content()
    urls = re.findall(r'href="(https://pitchfork\.com/reviews/albums/[^"]+)"', html)
    return urls[0] if urls else None


def scrape_review(browser, review_url):
    """抓取评论正文"""
    page = browser.new_context().new_page()
    page.goto(review_url)
    time.sleep(5)
    
    html = page.content()
    
    # 提取标题
    title_m = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
    title = title_m.group(1).strip() if title_m else ""
    
    # 提取评分
    score_m = re.search(r'class="[^"]*score[^"]*"[^>]*>([\d.]+)</', html)
    score = float(score_m.group(1)) if score_m else None
    
    # 提取作者
    author_m = re.search(r'class="[^"]*author[^"]*"[^>]*>([^<]+)</', html)
    author = author_m.group(1).strip() if author_m else ""
    
    # 提取正文（Pitchfork 用 <div class="contents"> 或类似）
    # 尝试多种选择器
    body = ""
    for pattern in [
        r'<div class="contents">(.*?)</div>\s*<footer',
        r'<div[^>]*id="contents"[^>]*>(.*?)</div>\s*<footer',
        r'<article[^>]*>(.*?)</article>',
    ]:
        m = re.search(pattern, html, re.DOTALL)
        if m:
            body = m.group(1)
            break
    
    # 清理 HTML 标签
    body = re.sub(r'<[^>]+>', '', body)
    body = re.sub(r'\s+', ' ', body).strip()
    
    return {
        'title': title,
        'score': score,
        'author': author,
        'url': review_url,
        'body': body[:5000]  # 限制长度
    }


def translate_text(text):
    """翻译（简易版，实际应调用翻译 API）"""
    # TODO: 接入翻译 API
    # 暂时返回原文
    return text


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

{review_data['body']}

## 译文

{translate_text(review_data['body'])}
"""
    
    filepath.write_text(md, encoding='utf-8')
    print(f"[PF] 评论已保存: {filepath}")
    return filepath


def main():
    if len(sys.argv) < 2:
        print("用法: python pf_review_scraper.py <album_id>")
        sys.exit(1)
    
    album_id = int(sys.argv[1])
    
    # 获取专辑信息
    import sqlite3
    conn = sqlite3.connect(DB)
    row = conn.execute("SELECT album_name, artist FROM albums WHERE album_id = ?", (album_id,)).fetchone()
    conn.close()
    
    if not row:
        print(f"[ERROR] 专辑 ID {album_id} 不存在")
        sys.exit(1)
    
    album_name, artist = row
    print(f"[PF] 处理: {artist} - {album_name}")
    
    # 获取 review URL
    review_url = get_review_url(album_id)
    
    if not review_url:
        print(f"[PF] 未找到 review_url，需要先搜索...")
        # 启动浏览器搜索
        browser = cloakbrowser.launch(headless=False)
        page = browser.new_page()
        page.goto("https://pitchfork.com/")
        time.sleep(10)
        
        review_url = search_pf_review(page, album_name, artist)
        browser.close()
        
        if not review_url:
            print(f"[ERROR] 无法找到评论 URL")
            sys.exit(1)
        
        # 保存 URL 到数据库
        conn = sqlite3.connect(DB)
        conn.execute("UPDATE albums SET review_url = ? WHERE album_id = ?", (review_url, album_id))
        conn.commit()
        conn.close()
        print(f"[PF] 已保存 review_url: {review_url}")
    
    # 抓取评论
    print(f"[PF] 抓取评论: {review_url}")
    browser = cloakbrowser.launch(headless=False)
    review_data = scrape_review(browser, review_url)
    browser.close()
    
    # 保存
    save_review(album_id, album_name, artist, review_data)
    print(f"[PF] 完成！")


if __name__ == "__main__":
    main()
