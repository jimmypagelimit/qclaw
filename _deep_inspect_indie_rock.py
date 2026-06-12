#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""仔细检查 indie-rock 页面的子流派区域 HTML"""
import time, re
from cloakbrowser import launch

browser = launch(headless=False)
page = browser.new_page()

print("[1] 首页过 CF...", flush=True)
page.goto("https://rateyourmusic.com/", timeout=90000)
time.sleep(25)

print("[2] 跳转 /genre/indie-rock/ ...", flush=True)
try:
    page.evaluate("window.location.href = '/genre/indie-rock/'")
except Exception:
    pass
time.sleep(18)

html = ''
for attempt in range(3):
    try:
        html = page.content()
        break
    except Exception:
        time.sleep(3)

print(f"页面大小: {len(html)}", flush=True)

# 搜索子流派区域的 HTML
# 先找 "Subgenres" 文字的位置
for keyword in ['Subgenres', 'subgenres', 'Children', 'children', 'Related']:
    idx = html.find(keyword)
    if idx >= 0:
        snippet = html[max(0,idx-500):idx+1000]
        print(f"\n找到 '{keyword}' 在位置 {idx}:", flush=True)
        print(snippet[:500], flush=True)
        break

# 搜索包含 genre 链接且 class 包含 page_features 的 div
print("\n\n搜索 page_features_secondary_metadata_genres 容器...", flush=True)
pattern = r'<div class="page_features_secondary_metadata_genres_primary[^"]*">.*?</div>'
matches = re.findall(pattern, html, re.DOTALL)
print(f"primary 容器数: {len(matches)}", flush=True)
for i, m in enumerate(matches[:3]):
    print(f"  [{i}] {m[:200]}", flush=True)

pattern2 = r'<div class="page_features_secondary_metadata_genres_secondary[^"]*">.*?</div>'
matches2 = re.findall(pattern2, html, re.DOTALL)
print(f"\nsecondary 容器数: {len(matches2)}", flush=True)
for i, m in enumerate(matches2[:3]):
    print(f"  [{i}] {m[:200]}", flush=True)

# 保存 HTML（前 50000 字符）供检查
with open(r'C:\Users\qujt\.qclaw\workspace\_indie_rock_full_html.txt', 'w', encoding='utf-8') as f:
    f.write(html[:100000])
print(f"\nHTML 前 100KB 已保存", flush=True)

browser.close()
print("完成", flush=True)
