#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在 rock HTML 中找子流派区域"""
import re

with open(r'C:\Users\qujt\.qclaw\workspace\_genre_rock.html', encoding='utf-8') as f:
    html = f.read()

print(f"HTML 大小: {len(html)}")

# 找所有可能的相关关键词
keywords = ['Subgenres', 'Children', 'subgenres', 'children', 'Sub-Genres', 'Child']
for kw in keywords:
    idx = html.find(kw)
    if idx >= 0:
        print(f"\n找到 '{kw}' 在位置 {idx}:")
        print(html[max(0,idx-300):idx+500])
        break
else:
    print("\n未找到 Subgenres/Children 关键词")
    # 打印页面标题区域
    idx = html.find('<h1')
    if idx >= 0:
        print("h1 区域:", html[idx:idx+500])
    
    # 找所有含 genre 的链接，看上下文
    print("\n找所有 genre 链接的上下文...")
    matches = list(re.finditer(r'href="/genre/([^"]+)/"', html))
    print(f"共 {len(matches)} 个 genre 链接")
    if matches:
        # 看第一个链接的上下文
        m = matches[0]
        ctx = html[max(0, m.start()-200):m.end()+200]
        print("第一个链接上下文:", ctx)
