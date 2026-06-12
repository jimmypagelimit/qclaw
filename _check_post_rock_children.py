#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查 post-rock 页面是否有子流派"""
import time, re, json
from cloakbrowser import launch

browser = launch(headless=False)
page = browser.new_page()

print("[1] 首页过 CF...", flush=True)
page.goto("https://rateyourmusic.com/", timeout=90000)
time.sleep(25)

print("[2] 跳转 /genre/post-rock/ ...", flush=True)
try:
    page.evaluate("window.location.href = '/genre/post-rock/'")
except Exception:
    pass
time.sleep(18)

print("[3] 检查子流派容器...", flush=True)

# 方法1: JS 精确查找子流派容器
result = page.evaluate("""
() => {
    const primary = document.getElementsByClassName('page_features_secondary_metadata_genres_primary');
    const secondary = document.getElementsByClassName('page_features_secondary_metadata_genres_secondary');
    const result = {
        primary_count: primary.length,
        secondary_count: secondary.length,
        primary_links: [],
        secondary_links: []
    };
    for (let i = 0; i < primary.length; i++) {
        const links = primary[i].querySelectorAll('a[href*="/genre/"]');
        for (let j = 0; j < links.length; j++) {
            result.primary_links.push({href: links[j].href, text: links[j].textContent.trim()});
        }
    }
    for (let i = 0; i < secondary.length; i++) {
        const links = secondary[i].querySelectorAll('a[href*="/genre/"]');
        for (let j = 0; j < links.length; j++) {
            result.secondary_links.push({href: links[j].href, text: links[j].textContent.trim()});
        }
    }
    return result;
}
""")

print(f"primary 容器: {result['primary_count']}", flush=True)
print(f"secondary 容器: {result['secondary_count']}", flush=True)
if result['primary_links']:
    print("primary 链接:", flush=True)
    for link in result['primary_links'][:10]:
        print(f"  {link['href']} -> {link['text']}", flush=True)
if result['secondary_links']:
    print("secondary 链接:", flush=True)
    for link in result['secondary_links'][:10]:
        print(f"  {link['href']} -> {link['text']}", flush=True)

# 方法2: 搜索页面 HTML 里的 "Children" 或 "Subgenres" 区域
html = ''
for attempt in range(3):
    try:
        html = page.content()
        break
    except Exception:
        time.sleep(3)

if html:
    for keyword in ['Children', 'Subgenres', 'children', 'subgenres']:
        idx = html.find(keyword)
        if idx >= 0:
            print(f"\n找到 '{keyword}' 在位置 {idx}", flush=True)
            print("周围 HTML:", html[max(0,idx-300):idx+500], flush=True)
            break

browser.close()
print("\n完成", flush=True)
