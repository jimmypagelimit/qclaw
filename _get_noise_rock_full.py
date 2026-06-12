#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""获取 noise-rock 页面的完整文本并搜索 parent/subgenre 信息"""
import time, re
from cloakbrowser import launch

browser = launch(headless=False)
page = browser.new_page()

print("[1] 首页过 CF...", flush=True)
page.goto("https://rateyourmusic.com/", timeout=90000)
time.sleep(25)

print("[2] 跳转 /genre/noise-rock/ ...", flush=True)
try:
    page.evaluate("window.location.href = '/genre/noise-rock/'")
except Exception:
    pass
time.sleep(18)

print("[3] 获取完整页面文本...", flush=True)
text = page.evaluate("() => document.body.innerText")

with open(r'C:\Users\qujt\.qclaw\workspace\_noise_rock_FULL.txt', 'w', encoding='utf-8') as f:
    f.write(text)
print(f"完整文本已保存 ({len(text)} 字符): _noise_rock_FULL.txt", flush=True)

# 搜索 parent/subgenre 关键词
print("\n[4] 搜索 parent/subgenre 关键词...", flush=True)
lines = text.split('\n')
for keyword in ['parent', 'Parent', 'subgenre of', 'Subgenre of', 'subgenres of', 'Subgenres of']:
    found = False
    for i, line in enumerate(lines):
        if keyword in line:
            print(f"  找到 '{keyword}' 在第 {i} 行:", flush=True)
            print(f"    {line}", flush=True)
            found = True
            break
    if not found:
        print(f"  未找到 '{keyword}'", flush=True)

# 也打印页面前 30 行看看结构
print("\n[5] 页面前 30 行:", flush=True)
for i, line in enumerate(lines[:30]):
    print(f"  {i}: {line}", flush=True)

browser.close()
print("\n完成", flush=True)
