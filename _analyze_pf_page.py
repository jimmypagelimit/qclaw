#!/usr/bin/env python3
"""分析 Pitchfork 页面结构"""
import urllib.request, re

url = "https://pitchfork.com/reviews/albums/aldous-harding-rain-on-the-island/"
print(f"抓取: {url}")

req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8')
    
    print(f"页面大小: {len(html)} 字节")
    
    # 检查关键元素
    print("\n=== 关键元素检查 ===")
    
    # 1. __PRELOADED_STATE__
    if '__PRELOADED_STATE__' in html:
        print("[✓] 找到 __PRELOADED_STATE__")
        m = re.search(r'__PRELOADED_STATE__\s*=\s*({.*?});', html, re.DOTALL)
        if m:
            print(f"  -> JSON 长度: {len(m.group(1))}")
    else:
        print("[✗] 未找到 __PRELOADED_STATE__")
    
    # 2. 标题
    title_m = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
    print(f"[标题] {title_m.group(1) if title_m else 'NOT FOUND'}")
    
    # 3. 评分
    score_patterns = [
        r'class="[^"]*score[^"]*"[^>]*>([\d.]+)</',
        r'"rating":\s*([\d.]+)',
        r'(\d\.\d)\s*<',
    ]
    for i, p in enumerate(score_patterns):
        m = re.search(p, html)
        if m:
            print(f"[评分] 模式{i+1}: {m.group(1)}")
            break
    else:
        print("[评分] NOT FOUND")
    
    # 4. 作者
    author_m = re.search(r'class="[^"]*author[^"]*"[^>]*>([^<]+)</', html)
    print(f"[作者] {author_m.group(1).strip() if author_m else 'NOT FOUND'}")
    
    # 5. 正文区域
    body_patterns = [
        r'<div[^>]*class="[^"]*body[^"]*"[^>]*>(.*?)</div>',
        r'<article[^>]*>(.*?)</article>',
        r'class="contents">(.*?)</div>\s*<footer',
    ]
    for i, p in enumerate(body_patterns):
        m = re.search(p, html, re.DOTALL)
        if m:
            body_len = len(m.group(1))
            print(f"[正文] 模式{i+1}: 找到 {body_len} 字符")
            break
    else:
        print("[正文] NOT FOUND")
    
    # 保存 HTML 用于分析
    with open('pf_page_debug.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\n调试 HTML 已保存: pf_page_debug.html")
    
except Exception as e:
    print(f"错误: {e}")
