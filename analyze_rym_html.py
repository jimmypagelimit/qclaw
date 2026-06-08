#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析 rym_album_click.html 的结构
找出专辑名、评分、评价数、流派的 HTML 模式
"""

import re

def analyze_html():
    with open('C:/Users/qujt/.qclaw/workspace/rym_album_click.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    print("=== 分析 RYM HTML 结构 ===\n")
    
    # 1. 专辑名 - 尝试多种模式
    print("[1] 专辑名:")
    
    # 模式1: <h1 class="album_title"><span>...</span></h1>
    m = re.search(r'<h1[^>]*class="album_title"[^>]*>(.*?)</h1>', html, re.DOTALL)
    if m:
        print(f"  模式1 (h1.album_title): {m.group(1)[:200]}")
    
    # 模式2: <title> 标签
    m = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
    if m:
        title_text = m.group(1)
        # 格式: "Album Name by Artist (Album, Genre): ..."
        album_match = re.search(r'^(.*?)\s+by\s+', title_text)
        if album_match:
            print(f"  模式2 (title tag): {album_match.group(1)}")
    
    # 模式3: og:title meta 标签
    m = re.search(r'property="og:title"\s+content="(.*?)"', html, re.DOTALL)
    if m:
        print(f"  模式3 (og:title): {m.group(1)[:200]}")
    
    # 2. 评分 - 尝试多种模式
    print("\n[2] 评分:")
    
    # 模式1: class="avg_rating"
    m = re.search(r'class="avg_rating"[^>]*>(.*?)</', html, re.DOTALL)
    if m:
        print(f"  模式1 (avg_rating): {m.group(1)[:100]}")
    
    # 模式2: 找数字 + / + 5
    m = re.search(r'(\d+\.\d+)\s*/\s*5', html)
    if m:
        print(f"  模式2 (数字/5): {m.group(1)}")
    
    # 模式3: 找 "Rated #" 后面的数字
    m = re.search(r'Rated\s+#(\d+)', html)
    if m:
        print(f"  模式3 (Rated #): #{m.group(1)}")
    
    # 3. 评价数
    print("\n[3] 评价数:")
    
    # 模式1: 数字 + "Ratings"
    m = re.search(r'([\d,]+)\s*Ratings?', html)
    if m:
        print(f"  模式1 (Ratings): {m.group(1)}")
    
    # 模式2: num_ratings class
    m = re.search(r'class="num_ratings"[^>]*>(.*?)</', html, re.DOTALL)
    if m:
        print(f"  模式2 (num_ratings): {m.group(1)[:100]}")
    
    # 4. 评论数
    print("\n[4] 评论数:")
    m = re.search(r'([\d,]+)\s*Reviews?', html)
    if m:
        print(f"  模式1 (Reviews): {m.group(1)}")
    
    # 5. 流派 (genre)
    print("\n[5] 流派 (genre):")
    genres = re.findall(r'href="/genre/([^"]+)"', html)
    if genres:
        # 去重
        seen = set()
        unique = []
        for g in genres:
            if g not in seen:
                seen.add(g)
                unique.append(g)
        print(f"  找到 {len(unique)} 个流派: {', '.join(unique[:10])}")
    
    # 6. 风格 (style)
    print("\n[6] 风格 (style):")
    styles = re.findall(r'href="/style/([^"]+)"', html)
    if styles:
        seen = set()
        unique = []
        for s in styles:
            if s not in seen:
                seen.add(s)
                unique.append(s)
        print(f"  找到 {len(unique)} 个风格: {', '.join(unique[:10])}")
    
    # 7. 艺人名
    print("\n[7] 艺人名:")
    
    # 模式1: class="artist"
    m = re.search(r'class="artist"[^>]*>(.*?)</', html, re.DOTALL)
    if m:
        print(f"  模式1 (class=artist): {m.group(1)[:200]}")
    
    # 模式2: og:title 里 "by" 后面
    m = re.search(r'by\s+([^-]+)\s+-', html)
    if m:
        print(f"  模式2 (og:title by): {m.group(1).strip()}")
    
    print("\n=== 分析完成 ===")
    print("如果某个字段显示 '未找到'，需要检查 HTML 结构或改用 page.evaluate()")

if __name__ == '__main__':
    analyze_html()
