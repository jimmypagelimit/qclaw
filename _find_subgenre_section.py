#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用 Playwright locator 找 genre 页面的子流派区域"""
import time
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

print("[3] 查找子流派区域...", flush=True)

# 尝试找包含 "Subgenres" 文字的元素
for selector in [
    'text="Subgenres"',
    'text=/Subgenres/i',
    '.genre_children',
    '.subgenres',
    '#subgenres',
    'h2:has-text("Subgenres")',
    'h3:has-text("Subgenres")',
]:
    try:
        elem = page.locator(selector)
        if elem.count() > 0:
            print(f"  找到: {selector} (count={elem.count()})", flush=True)
            # 获取周围 HTML
            html = elem.first.evaluate("el => el.outerHTML")
            print(f"  HTML 样本 (200字): {html[:200]}", flush=True)
    except Exception as e:
        pass

# 找所有 genre 链接，看它们在页面的什么位置
print("\n[4] 找所有 genre 链接的父容器...", flush=True)
links = page.locator('a[href*="/genre/"]')
cnt = links.count()
print(f"  共 {cnt} 个 genre 链接", flush=True)

if cnt > 0:
    # 取前5个，看它们的父容器 class
    for i in range(min(5, cnt)):
        try:
            parent_class = links.nth(i).evaluate("el => el.parentElement?.className || ''")
            href = links.nth(i).get_attribute('href')
            text = links.nth(i).text_content()
            print(f"  [{i}] {href} | parent class: {parent_class} | text: {text}", flush=True)
        except Exception as e:
            pass

# 截图
png = r'C:\Users\qujt\.qclaw\workspace\_indie_rock_full.png'
page.screenshot(path=png, full_page=True)
print(f"\n[5] 全页截图: {png}", flush=True)

browser.close()
print("完成", flush=True)
