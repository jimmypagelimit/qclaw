#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查 rock 页面子流派容器的精确 HTML 结构"""
import time, re
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

print("[3] 用 JS 精确查找子流派容器...", flush=True)

# 方法1: 直接找 class 精确匹配的容器
result = page.evaluate("""
() => {
    const primary = document.getElementsByClassName('page_features_secondary_metadata_genres_primary');
    const secondary = document.getElementsByClassName('page_features_secondary_metadata_genres_secondary');
    return {
        primary_count: primary.length,
        secondary_count: secondary.length,
        primary_html: primary.length > 0 ? primary[0].outerHTML.slice(0, 500) : 'NONE',
        secondary_html: secondary.length > 0 ? secondary[0].outerHTML.slice(0, 500) : 'NONE'
    };
}
""")

print(f"primary 容器数: {result['primary_count']}", flush=True)
print(f"secondary 容器数: {result['secondary_count']}", flush=True)
print(f"\nprimary 样本 HTML:", flush=True)
print(result['primary_html'][:300], flush=True)
print(f"\nsecondary 样本 HTML:", flush=True)
print(result['secondary_html'][:300], flush=True)

# 方法2: 找页面上所有包含 "page_features_secondary_metadata_genres" 的元素
print("\n[4] 找所有包含该 class 字符串的元素...", flush=True)
result2 = page.evaluate("""
() => {
    const all = document.querySelectorAll('[class*="page_features_secondary_metadata_genres"]');
    const items = [];
    for (let i = 0; i < Math.min(all.length, 5); i++) {
        const el = all[i];
        const links = el.querySelectorAll('a[href*="/genre/"]');
        const linkData = [];
        for (let j = 0; j < links.length; j++) {
            linkData.push({href: links[j].href, text: links[j].textContent.trim()});
        }
        items.push({
            class: el.className,
            tag: el.tagName,
            link_count: links.length,
            links: linkData.slice(0, 3)
        });
    }
    return {total: all.length, items: items};
}
""")

print(f"包含该 class 的元素数: {result2['total']}", flush=True)
for item in result2['items']:
    print(f"  class={item['class'][:80]} | tag={item['tag']} | {item['link_count']} 个链接", flush=True)
    for link in item['links']:
        print(f"    {link['href']} -> {link['text']}", flush=True)

browser.close()
print("\n完成", flush=True)
