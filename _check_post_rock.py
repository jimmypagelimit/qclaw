#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查 post-rock 页面是否有子流派"""
import time, json
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

print("[3] 用 JS 提取子流派...", flush=True)
try:
    slugs = page.evaluate("""
    () => {
        const containers = document.querySelectorAll('[class*="page_features_secondary_metadata_genres_"]');
        const seen = new Set();
        containers.forEach(container => {
            const links = container.querySelectorAll('a[href*="/genre/"]');
            links.forEach(link => {
                const m = link.href.match(/\\/genre\\/([^\\/]+)\\//);
                if (m) seen.add(m[1]);
            });
        });
        return { count: seen.size, slugs: Array.from(seen) };
    }
    """)
    print(f"  结果: {slugs}", flush=True)
except Exception as e:
    print(f"  JS 失败: {e}", flush=True)

# 也检查页面 HTML 里有没有子流派链接
html = ''
for attempt in range(3):
    try:
        html = page.content()
        break
    except Exception:
        time.sleep(3)

if html:
    import re
    all_genre_links = re.findall(r'href="/genre/([^"]+)/"', html)
    unique = list(set(all_genre_links))
    print(f"\n  HTML 中全部 genre 链接: {len(unique)} 个", flush=True)
    print(f"  样本: {unique[:15]}", flush=True)

browser.close()
print("完成", flush=True)
