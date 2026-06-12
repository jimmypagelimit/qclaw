#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""看 rock 页面的完整文本，找子流派区域（输出到文件）"""
import time, sys
from cloakbrowser import launch

sys.stdout.reconfigure(encoding='utf-8')  # 强制 UTF-8 输出

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

text = page.evaluate("() => document.body.innerText")
print(f"文本长度: {len(text)}", flush=True)

# 保存完整文本到文件
with open(r'C:\Users\qujt\.qclaw\workspace\_rock_page_text.txt', 'w', encoding='utf-8') as f:
    f.write(text)
print("完整文本已保存: _rock_page_text.txt", flush=True)

# 找 "Subgenres" 或 "Children"
lines = text.split('\n')
for i, line in enumerate(lines):
    if 'Subgenres' in line or 'Children' in line or 'subgenres' in line or 'children' in line:
        print(f"\n找到关键词在第 {i} 行", flush=True)
        # 打印前后 10 行到文件
        with open(r'C:\Users\qujt\.qclaw\workspace\_rock_context.txt', 'w', encoding='utf-8') as f:
            start = max(0, i-5)
            end = min(len(lines), i+20)
            for j in range(start, end):
                f.write(f"{j}: {lines[j]}\n")
        print(f"上下文已保存: _rock_context.txt", flush=True)
        break
else:
    print("\n未找到 Subgenres/Children 关键词", flush=True)
    # 打印前 50 行到文件
    with open(r'C:\Users\qujt\.qclaw\workspace\_rock_first_50_lines.txt', 'w', encoding='utf-8') as f:
        for j in range(min(50, len(lines))):
            f.write(f"{j}: {lines[j]}\n")
    print("前 50 行已保存: _rock_first_50_lines.txt", flush=True)

browser.close()
print("完成", flush=True)
