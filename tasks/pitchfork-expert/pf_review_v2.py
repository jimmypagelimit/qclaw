#!/usr/bin/env python3
"""正确提取 Pitchfork 评论（从 __PRELOADED_STATE__）"""
import sys, json, re, time
import urllib.request
from pathlib import Path

DB = Path(r"C:\Users\qujt\.qclaw\workspace\_music_latest.db")
REVIEWS_DIR = Path(r"C:\Users\qujt\.qclaw\workspace\tasks\pitchfork-expert\docs\reviews")
REVIEWS_DIR.mkdir(parents=True, exist_ok=True)


def fetch_html(url):
    """获取 HTML"""
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode('utf-8')


def extract_state(html):
    """提取 __PRELOADED_STATE__ JSON"""
    # 方法1: 直接正则
    m = re.search(r'__PRELOADED_STATE__\s*=\s*({.*?})\s*;', html, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except:
            pass
    
    # 方法2: 找最后一个大的 {...}`（更复杂但更可靠）
    # 先找到所有 __PRELOADED_STATE__ 的位置
    pattern = r'__PRELOADED_STATE__\s*=\s*'
    start = html.find(pattern)
    if start == -1:
        return None
    
    # 跳过 pattern
    start += len(pattern)
    
    # 找到匹配的 }（处理嵌套）
    depth = 0
    in_string = False
    escape_next = False
    i = start
    
    while i < len(html):
        c = html[i]
        
        if escape_next:
            escape_next = False
            i += 1
            continue
            
        if c == '\\' and in_string:
            escape_next = True
            i += 1
            continue
            
        if c == '"' and not escape_next:
            in_string = not in_string
        elif not in_string:
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    # 找到匹配的 }
                    try:
                        return json.loads(html[start:i+1])
                    except:
                        return None
        
        i += 1
    
    return None


def parse_review(data):
    """从 __PRELOADED_STATE__ 解析评论数据"""
    # Pitchfork 的数据结构可能是：
    # data['props']['pageProps']['review'] 
    # 或者 data['pageProps']['review']
    # 等等
    
    def find_review(obj, depth=0):
        """递归查找 review 数据"""
        if depth > 10:
            return None
        
        if isinstance(obj, dict):
            # 检查是否包含 review 相关字段
            if 'rating' in obj and 'title' in obj:
                return obj
            
            # 递归查找
            for v in obj.values():
                result = find_review(v, depth + 1)
                if result:
                    return result
                    
        elif isinstance(obj, list):
            for item in obj:
                result = find_review(item, depth + 1)
                if result:
                    return result
                    
        return None
    
    return find_review(data)


def scrape_review(url):
    """抓取评论"""
    print(f"  -> 获取 HTML: {url}")
    html = fetch_html(url)
    print(f"  -> HTML 大小: {len(html)} 字节")
    
    # 提取 __PRELOADED_STATE__
    print("  -> 提取 __PRELOADED_STATE__...")
    data = extract_state(html)
    
    if not data:
        print("  -> 未找到 __PRELOADED_STATE__，尝试正则提取...")
        return extract_fallback(html, url)
    
    # 解析评论数据
    print("  -> 解析评论数据...")
    review = parse_review(data)
    
    if not review:
        print("  -> 未找到评论数据，尝试正则提取...")
        return extract_fallback(html, url)
    
    # 提取字段
    result = {
        'title': review.get('title', ''),
        'score': review.get('rating', 0),
        'author': review.get('author', {}).get('name', '') if isinstance(review.get('author'), dict) else '',
        'body': review.get('body', ''),
        'url': url
    }
    
    # 如果 body 为空，尝试从 HTML 提取
    if not result['body']:
        result['body'] = extract_body_fallback(html)
    
    return result


def extract_fallback(html, url):
    """正则提取（备用方案）"""
    result = {'url': url, 'body': ''}
    
    # 标题
    m = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
    result['title'] = m.group(1).strip() if m else ''
    
    # 评分
    m = re.search(r'class="[^"]*score[^"]*"[^>]*>([\d.]+)</', html)
    if not m:
        m = re.search(r'"rating":\s*([\d.]+)', html)
    result['score'] = float(m.group(1)) if m else 0
    
    # 作者
    m = re.search(r'class="[^"]*author[^"]*"[^>]*>([^<]+)</', html)
    result['author'] = m.group(1).strip() if m else ''
    
    # 正文
    result['body'] = extract_body_fallback(html)
    
    return result


def extract_body_fallback(html):
    """从 HTML 提取正文（正则）"""
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


def translate_text(text):
    """翻译（占位）"""
    return f"[译文待补充]\n\n{text[:500]}..."


def save_review(album_id, album_name, artist, review_data):
    """保存评论"""
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
        print("用法: python pf_review_v2.py <album_id>")
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
    
    # 如果已有 review_url，直接使用
    if review_url:
        print(f"  -> 使用已有 URL: {review_url}")
        url = review_url
    else:
        # 构造 URL
        url = f"https://pitchfork.com/reviews/albums/{artist.lower().replace(' ', '-')}-{album_name.lower().replace(' ', '-')}/"
        print(f"  -> 尝试 URL: {url}")
    
    # 抓取评论
    review_data = scrape_review(url)
    
    if not review_data:
        print(f"[ERROR] 抓取失败")
        sys.exit(1)
    
    # 保存
    save_review(album_id, album_name, artist, review_data)
    
    # 更新数据库
    conn.execute(
        "UPDATE albums SET review_url = ? WHERE album_id = ?",
        (review_data['url'], album_id)
    )
    conn.commit()
    conn.close()
    
    print(f"[PF] 完成！")


if __name__ == "__main__":
    main()
