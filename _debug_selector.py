#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug: 找 indie-rock 页面子流派的正确选择器"""
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

print("[3] 调试选择器...", flush=True)

# 方法1: 找所有包含 genre 链接的容器
print("\n方法1: 找 class 包含 'genre' 的容器...", flush=True)
containers = page.locator('[class*="genre"]')
cnt = containers.count()
print(f"  找到 {cnt} 个容器", flush=True)
for i in range(min(cnt, 10)):
    try:
        cls = containers.nth(i).get_attribute('class')
        html = containers.nth(i).evaluate("el => el.outerHTML")[:300]
        links = containers.nth(i).locator('a[href*="/genre/"]')
        n_links = links.count()
        print(f"  [{i}] class={cls[:80]} | 内含 {n_links} 个 genre 链接", flush=True)
        if n_links > 0:
            href = links.first.get_attribute('href')
            text = links.first.text_content()
            print(f"      样本: {href} -> {text}", flush=True)
    except Exception as e:
        pass

# 方法2: 直接找所有 genre 链接，看它们的父元素
print("\n方法2: 所有 genre 链接的父元素 class...", flush=True)
all_links = page.locator('a[href*="/genre/"]')
cnt = all_links.count()
print(f"  共 {cnt} 个 genre 链接", flush=True)
parent_classes = set()
for i in range(min(cnt, 20)):
    try:
        parent_class = all_links.nth(i).evaluate("el => el.parentElement?.className || ''")
        parent_classes.add(parent_class)
    except Exception:
        pass
print(f"  前20个链接的父 class (去重):", flush=True)
for pc in sorted(parent_classes)[:10]:
    print(f"    {pc}", flush=True)

# 方法3: 执行 JS 找子流派区域
print("\n方法3: JS 找 'Subgenres' 附近的元素...", flush=True)
try:
    result = page.evaluate("""
    () => {
        // 找包含 "Subgenres" 文字的元素
        const all = document.querySelectorAll('*');
        for (let el of all) {
            if (el.textContent.includes('Subgenres') && el.children.length > 0) {
                return el.outerHTML.slice(0, 500);
            }
        }
        return 'Not found';
    }
    """)
    print(f"  结果: {result[:300]}", flush=True)
except Exception as e:
    print(f"  JS 执行失败: {e}", flush=True)

browser.close()
print("\n完成", flush=True)
