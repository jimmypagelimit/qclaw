#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""分析 indie-rock 页面的子流派区域 HTML 结构"""
import re

with open(r'C:\Users\qujt\.qclaw\workspace\_indie_rock_page.html', encoding='utf-8') as f:
    html = f.read()

print(f"HTML 大小: {len(html)}", flush=True)

# 找 "Subgenres" 或相关标题
for pattern in [r'Subgenres', r'subgenres', r'子流派']:
    idx = html.find(pattern)
    if idx >= 0:
        print(f"\n找到 '{pattern}' 在位置 {idx}", flush=True)
        print("周围 HTML:", html[max(0,idx-200):idx+500], flush=True)
        break
else:
    print("未找到 Subgenres 关键词，尝试找 genre 列表...", flush=True)

# 找所有包含 genre 的链接，看上下文
# 先找 <div 或 <section 包含 genre 相关类名的
genre_divs = re.findall(r'<(div|section|ul)[^>]*(?:class|id)="[^"]*genre[^"]*"[^>]*>(.*?)</\1>', html, re.DOTALL | re.IGNORECASE)
print(f"\n找到 {len(genre_divs)} 个 genre 相关容器", flush=True)
for i, (tag, content) in enumerate(genre_divs[:3]):
    links = re.findall(r'href="/genre/([^"]+)/"', content)
    print(f"  容器{i+1}: {len(links)} 个 genre 链接", flush=True)
    if links:
        print(f"    前5个: {links[:5]}", flush=True)

# 直接搜索 "indie-rock" 的子流派：找链接文本中包含 indie 的
print("\n尝试找子流派链接的唯一模式...", flush=True)
# RYM 子流派页面的链接格式：/genre/xxx/，其中 xxx 可能包含父 slug
# 比如 indie-rock 的子流派可能是 indie-rock/* 或完全独立的 slug

# 打印所有 unique genre slug
all_slugs = list(set(re.findall(r'href="/genre/([^"]+)/"', html)))
print(f"全部 {len(all_slugs)} 个 unique genre slug", flush=True)
print("样本:", sorted(all_slugs)[:30], flush=True)
