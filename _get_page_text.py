#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""看 rock 页面的完整文本，找子流派区域"""
import time
from cloakbrowser import launch

browser = launch(headless=False)
page = browser.new_page()

print("[1] 首页过 CF...", flush=True)
page.goto("https://rateyourmusic.com/", timeout=90000)
time.sleep(25)

print("[2] 跳转 /genre/rock/ ...", flush=True)
try:
    page.evaluate("window.location.href = '/genre/rock/'")
except Exception:
    pass
time.sleep(18)

print("[3] 获取页面完整文本...", flush=True)

# 获取页面完整文本内容
text = page.evaluate("() => document.body.innerText")
print(f"文本长度: {len(text)}", flush=True)

# 找 "Subgenres" 或 "Children"
lines = text.split('\n')
for i, line in enumerate(lines):
    if 'Subgenres' in line or 'Children' in line or 'subgenres' in line or 'children' in line:
        print(f"\n找到关键词在第 {i} 行:", flush=True)
        # 打印前后 10 行
        start = max(0, i-3)
        end = min(len(lines), i+15)
        for j in range(start, end):
            print(f"  {j}: {lines[j]}", flush=True)
        break
else:
    print("\n未找到 Subgenres/Children 关键词", flush=True)
    # 打印前 50 行看看页面结构
    print("\n页面前 50 行文本:", flush=True)
    for j in range(min(50, len(lines))):
        print(f"  {j}: {lines[j]}", flush=True)

browser.close()
print("\n完成", flush=True)
