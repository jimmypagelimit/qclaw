#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试 RYM JS 跳转 - 最简方案"""
import time
from cloakbrowser import launch

browser = launch(headless=False)
page = browser.new_page()

print("[1] page.goto + sleep(20) ...", flush=True)
page.goto("https://rateyourmusic.com/", timeout=90000)
time.sleep(25)  # 比之前多5秒

print(f"  URL: {page.url}", flush=True)
print(f"  title: {page.title()}", flush=True)

print("[2] JS 跳转 /artist/slint/ ...", flush=True)
try:
    page.evaluate("window.location.href = '/artist/slint/'")
except Exception as e:
    pass  # 导航销毁上下文正常
time.sleep(15)

print(f"  URL: {page.url}", flush=True)
print(f"  title: {page.title()}", flush=True)

html = page.content()
print(f"  页面大小: {len(html)}", flush=True)

if len(html) > 73000:
    print("  成功！", flush=True)
    with open(r'C:\Users\qujt\.qclaw\workspace\_slint_ok.html', 'w', encoding='utf-8') as f:
        f.write(html)
else:
    print("  失败", flush=True)

browser.close()
print("完成")
