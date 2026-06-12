#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RYM 搜索+进入专辑页 - 增加等待时间"""

import sys, time, json, re
from cloakbrowser import launch

ALBUM = "Beauty Land"
ARTIST = "Greg Mendez"

print("=== RYM 搜索调试 v2 ===\n")

browser = launch(headless=False)
page = browser.new_page()

# 首页过 CF
print("[1/4] 访问首页 (等待 CF 20秒)...")
page.goto("https://rateyourmusic.com/", timeout=90000)
time.sleep(20)
print("  -> CF challenge 完成")

# 搜索
print(f"\n[2/4] 搜索: {ALBUM} {ARTIST}")
search_box = page.locator("#ui_search_input_main_search").first
search_box.click()
time.sleep(0.5)
search_box.fill("")
time.sleep(0.3)
search_box.type(f"{ALBUM} {ARTIST}", delay=60)
time.sleep(0.5)
search_box.press("Enter")
print("  -> 已按 Enter，等待搜索结果加载...")

# 等待搜索结果加载（等待 .search_results 出现）
try:
    page.wait_for_selector(".search_results, .ui_search_results", timeout=15000)
    print("  -> 搜索结果容器已加载")
except:
    print("  -> 未找到搜索结果容器，继续等待...")
    time.sleep(10)

# 额外等待让 JS 渲染
time.sleep(10)
print("  -> 等待完成")

# 保存 HTML
html = page.content()
print(f"\n[3/4] HTML 大小: {len(html)} bytes")
with open("rym_search_v2.html", "w", encoding="utf-8") as f:
    f.write(html)
print("  -> 保存: rym_search_v2.html")

# 查找 /release/ 链接
links = re.findall(r'href="(/release/[^"]+)"', html)
print(f"  -> 找到 {len(links)} 个 /release/ 链接:")
for i, link in enumerate(links[:10], 1):
    print(f"     [{i}] {link}")

# 查找所有 a 标签文本
a_tags = re.findall(r'<a[^>]+href="([^"]*)"[^>]*>([^<]*)</a>', html)
print(f"\n  -> 找到 {len(a_tags)} 个 <a> 标签")
release_a = [(href, text) for href, text in a_tags if '/release/' in href]
print(f"  -> 其中 {len(release_a)} 个包含 /release/")
for href, text in release_a[:10]:
    print(f"     {text[:50]} -> {href}")

# JS click 进入第一个专辑
print("\n[4/4] JS click 进入专辑页...")
if links:
    # 直接 goto 第一个专辑链接
    first_link = links[0]
    full_url = f"https://rateyourmusic.com{first_link}"
    print(f"  -> 直接 goto: {full_url}")
    page.goto(full_url, timeout=60000)
    time.sleep(15)
    
    album_html = page.content()
    print(f"  -> 专辑页 HTML: {len(album_html)} bytes")
    
    if len(album_html) > 73000:
        print("  -> [成功] 专辑页加载正常")
        page.screenshot(path="rym_album_v2.png", full_page=True)
        print("  -> 截图: rym_album_v2.png")
        
        with open("rym_album_v2.html", "w", encoding="utf-8") as f:
            f.write(album_html)
        print("  -> 保存: rym_album_v2.html")
    else:
        print("  -> [CF 拦截] 专辑页被阻止")
else:
    print("  -> 未找到专辑链接，JS click 方案...")
    js_click = """() => {
        const links = document.querySelectorAll('a[href*="/release/"]');
        if (links.length > 0) { links[0].click(); return true; }
        return false;
    }"""
    result = page.evaluate(js_click)
    print(f"  -> JS click: {result}")
    time.sleep(15)
    
    album_html = page.content()
    print(f"  -> 专辑页 HTML: {len(album_html)} bytes")

print("\n关闭浏览器...")
browser.close()
print("完成！")
