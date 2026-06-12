#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查 RYM 流派浏览页 (/genre/) 的树形结构"""
import time, re, json
from cloakbrowser import launch

browser = launch(headless=False)
page = browser.new_page()

print("[1] 首页过 CF...", flush=True)
page.goto("https://rateyourmusic.com/", timeout=90000)
time.sleep(25)

print("[2] 跳转 /genre/ ...", flush=True)
try:
    page.evaluate("window.location.href = '/genre/'")
except Exception:
    pass
time.sleep(18)

print("[3] 检查页面结构...", flush=True)

# 获取页面 HTML
html = ''
for attempt in range(3):
    try:
        html = page.content()
        break
    except Exception:
        time.sleep(3)

print(f"页面大小: {len(html)}", flush=True)

# 保存 HTML
with open(r'C:\Users\qujt\.qclaw\workspace\_genre_browse.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("HTML 已保存: _genre_browse.html", flush=True)

# 查找树形结构
print("\n[4] 查找树形结构...", flush=True)
result = page.evaluate("""
() => {
    // 找所有包含 genre 的链接
    const allLinks = document.querySelectorAll('a[href*="/genre/"]');
    const links = [];
    for (let i = 0; i < allLinks.length; i++) {
        const link = allLinks[i];
        const href = link.href;
        const text = link.textContent.trim();
        const m = href.match(/\\/genre\\/([^\\/]+)\\//);
        if (m) {
            links.push({slug: m[1], text: text, href: href});
        }
    }
    
    // 找所有可能的树形容器
    const trees = document.querySelectorAll('[class*="tree"], [class*="genre_list"], [class*="genre_browse"]');
    const treeInfo = [];
    for (let i = 0; i < trees.length; i++) {
        treeInfo.push({
            tag: trees[i].tagName,
            class: trees[i].className,
            childCount: trees[i].children.length
        });
    }
    
    return {linkCount: links.length, links: links.slice(0, 30), treeCount: trees.length, treeInfo: treeInfo};
}
""")

print(f"  找到 {result['linkCount']} 个 genre 链接", flush=True)
print(f"  树形容器数: {result['treeCount']}", flush=True)
if result['treeInfo']:
    print("  树形容器:", flush=True)
    for t in result['treeInfo'][:5]:
        print(f"    {t['tag']}: {t['class'][:80]} | {t['childCount']} 子元素", flush=True)

print("\n  前30个 genre 链接:", flush=True)
for link in result['links'][:30]:
    print(f"    /genre/{link['slug']}/ -> {link['text']}", flush=True)

# 截图
png = r'C:\Users\qujt\.qclaw\workspace\_genre_browse.png'
page.screenshot(path=png, full_page=True)
print(f"\n[5] 全页截图: {png}", flush=True)

browser.close()
print("完成", flush=True)
