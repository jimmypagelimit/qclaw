#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查 indie-rock 是否有子流派（验证多层结构）"""
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

# 找所有 genre 链接
pattern = r'href="/genre/([^"]+)/"'
all_matches = re.findall(pattern, html)
print(f"\n所有 genre 链接数: {len(all_matches)}", flush=True)

# 去重
unique = list(set(all_matches))
print(f"去重后: {len(unique)}", flush=True)
print(f"\n前20个 genre slug:", flush=True)
for s in unique[:20]:
    print(f"  /genre/{s}/", flush=True)

# 保存 HTML 供检查
with open(r'C:\Users\qujt\.qclaw\workspace\_indie_rock_page.html', 'w', encoding='utf-8') as f:
    f.write(html)
print(f"\nHTML 已保存，可检查子流派区域", flush=True)

browser.close()
print("完成", flush=True)
