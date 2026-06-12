#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""找 RYM 流派页面真正的子流派区域"""
import time, re
from cloakbrowser import launch

def find_subgenre_section(page, slug):
    """用 JS 找子流派区域"""
    result = page.evaluate("""
    (slug) => {
        // 找包含 "Subgenres of" 或 "Children of" 的标题元素
        const headings = document.querySelectorAll('h1, h2, h3, h4, .section_heading, .page_section_heading');
        const found = [];
        for (let h of headings) {
            const text = h.textContent.trim();
            if (text.includes('Subgenres') || text.includes('Children') || text.includes('Related')) {
                found.push({
                    tag: h.tagName,
                    text: text,
                    html: h.outerHTML,
                    nextSibling: h.nextElementSibling ? h.nextElementSibling.className : 'NONE'
                });
            }
        }
        return { headings: found, url: window.location.href };
    }
    """, slug)
    return result

browser = launch(headless=False)
page = browser.new_page()

print("[1] 首页过 CF...", flush=True)
page.goto("https://rateyourmusic.com/", timeout=90000)
time.sleep(25)

# 测试几个流派页面
for slug in ['rock', 'indie-rock', 'post-rock', 'noise-rock']:
    print(f"\n[{slug}] 跳转...", flush=True)
    try:
        page.evaluate(f'window.location.href = "/genre/{slug}/"')
    except Exception:
        pass
    time.sleep(18)
    
    result = find_subgenre_section(page, slug)
    print(f"  URL: {result['url']}", flush=True)
    print(f"  找到 {len(result['headings'])} 个标题", flush=True)
    for h in result['headings'][:3]:
        print(f"    {h['tag']}: {h['text'][:80]}", flush=True)
        print(f"    nextSibling class: {h['nextSibling']}", flush=True)
    
    # 也尝试直接找页面上所有 genre 链接，看哪些是子流派
    html = ''
    for attempt in range(3):
        try:
            html = page.content()
            break
        except Exception:
            time.sleep(3)
    
    if html:
        # 统计 unique genre 链接
        all_links = re.findall(r'href="/genre/([^"]+)/"', html)
        unique = list(set(all_links))
        print(f"  页面共 {len(unique)} 个 unique genre 链接", flush=True)
        
        # 保存 HTML 前 50000 字符供检查
        with open(f'C:/Users/qujt/.qclaw/workspace/_genre_{slug}.html', 'w', encoding='utf-8') as f:
            f.write(html[:100000])
        print(f"  HTML 已保存: _genre_{slug}.html", flush=True)

browser.close()
print("\n完成", flush=True)
