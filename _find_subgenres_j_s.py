#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用 JS 在 rock 页面找子流派区域（通过文本内容）"""
import time, re, json
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

print("[3] 用 JS 找子流派区域...", flush=True)

result = page.evaluate("""
() => {
    // 方法1: 找所有包含 "Subgenres" 或 "Children" 的元素的父容器
    const all = document.querySelectorAll('*');
    const sections = [];
    for (let el of all) {
        const text = el.textContent;
        if ((text.includes('Subgenres') || text.includes('Children of')) && el.children.length > 0) {
            // 找这个元素后面紧跟的 genre 链接
            let next = el.nextElementSibling;
            const links = [];
            while (next && links.length === 0) {
                const aLinks = next.querySelectorAll ? next.querySelectorAll('a[href*="/genre/"]') : [];
                for (let j = 0; j < aLinks.length; j++) {
                    links.push({href: aLinks[j].href, text: aLinks[j].textContent.trim()});
                }
                next = next.nextElementSibling;
            }
            sections.push({
                tag: el.tagName,
                text: el.textContent.trim().slice(0, 100),
                linkCount: links.length,
                links: links.slice(0, 10)
            });
        }
    }
    
    // 方法2: 找页面上所有 genre 链接，按出现顺序分组
    const allGenreLinks = document.querySelectorAll('a[href*="/genre/"]');
    const linkGroups = [];
    let currentGroup = null;
    for (let i = 0; i < allGenreLinks.length; i++) {
        const link = allGenreLinks[i];
        const href = link.href;
        const text = link.textContent.trim();
        const m = href.match(/\\/genre\\/([^\\/]+)\\//);
        if (!m) continue;
        
        // 检查这个链接是否在某个带 class 的容器内
        let container = link.parentElement;
        let depth = 0;
        while (container && depth < 5) {
            if (container.className && container.className.includes('genre')) {
                const cls = container.className;
                if (!currentGroup || currentGroup.className !== cls) {
                    currentGroup = {className: cls, links: []};
                    linkGroups.push(currentGroup);
                }
                currentGroup.links.push({slug: m[1], text: text});
                break;
            }
            container = container.parentElement;
            depth++;
        }
    }
    
    return {sections: sections, linkGroups: linkGroups.slice(0, 10)};
}
""")

print(f"方法1: 找到 {len(result['sections'])} 个可能的子流派区域", flush=True)
for sec in result['sections']:
    print(f"  {sec['tag']}: {sec['text']}", flush=True)
    print(f"    后接 {sec['linkCount']} 个链接", flush=True)
    for link in sec['links'][:5]:
        print(f"      {link['href']} -> {link['text']}", flush=True)

print(f"\n方法2: 找到 {len(result['linkGroups'])} 个链接组", flush=True)
for grp in result['linkGroups'][:5]:
    print(f"  容器 class: {grp['className'][:80]}", flush=True)
    print(f"    {len(grp['links'])} 个链接: {[l['slug'] for l in grp['links'][:5]]}", flush=True)

browser.close()
print("\n完成", flush=True)
