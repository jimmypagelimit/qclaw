#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""调试：检查 RYM 搜索结果页面结构"""

import sys, time, re
from cloakbrowser import launch

print("=== RYM 搜索结果调试 ===\n")

browser = launch(headless=False)
page = browser.new_page()

# 首页过 CF
print("[1/3] 访问首页 (等待 CF 20秒)...")
page.goto("https://rateyourmusic.com/", timeout=90000)
time.sleep(20)
print("  -> CF challenge 完成")

# 搜索
print("\n[2/3] 搜索: Beauty Land Greg Mendez")
search_box = page.locator("#ui_search_input_main_search").first
search_box.click()
time.sleep(0.5)
search_box.fill("")
time.sleep(0.3)
search_box.type("Beauty Land Greg Mendez", delay=60)
time.sleep(0.5)
search_box.press("Enter")
time.sleep(12)
print("  -> 搜索完成")

# 保存搜索结果页 HTML
html = page.content()
print(f"\n  -> HTML 大小: {len(html)} bytes")
with open("rym_search_result.html", "w", encoding="utf-8") as f:
    f.write(html)
print("  -> 保存: rym_search_result.html")

# 查找所有 /release/ 链接
links = re.findall(r'href="(/release/[^"]+)"', html)
print(f"\n  -> 找到 {len(links)} 个 /release/ 链接:")
for i, link in enumerate(links[:10], 1):
    print(f"     [{i}] {link}")

# 查找所有 a 标签
a_tags = re.findall(r'<a[^>]+href="([^"]*)"[^>]*>([^<]*)</a>', html)
print(f"\n  -> 找到 {len(a_tags)} 个 <a> 标签")
release_links = [(href, text) for href, text in a_tags if '/release/' in href]
print(f"  -> 其中 {len(release_links)} 个包含 /release/")
for href, text in release_links[:10]:
    print(f"     {text[:50]} -> {href}")

# 截图
page.screenshot(path="rym_search_result.png", full_page=True)
print("\n  -> 截图: rym_search_result.png")

print("\n[3/3] 关闭浏览器...")
browser.close()
print("完成！")
