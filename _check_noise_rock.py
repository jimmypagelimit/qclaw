#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查 noise-rock 页面，看它是否有父流派链接（验证多层结构）"""
import time, re
from cloakbrowser import launch

browser = launch(headless=False)
page = browser.new_page()

print("[1] 首页过 CF...", flush=True)
page.goto("https://rateyourmusic.com/", timeout=90000)
time.sleep(25)

print("[2] 跳转 /genre/noise-rock/ ...", flush=True)
try:
    page.evaluate("window.location.href = '/genre/noise-rock/'")
except Exception:
    pass
time.sleep(18)

print("[3] 找父流派链接...", flush=True)

# 方法1: 找页面上所有指向 /genre/ 的链接，看哪些是 noise-rock 的父流派
result = page.evaluate("""
() => {
    // 找所有 genre 链接
    const allLinks = document.querySelectorAll('a[href*="/genre/"]');
    const links = [];
    for (let i = 0; i < allLinks.length; i++) {
        const link = allLinks[i];
        const href = link.href;
        const text = link.textContent.trim();
        const m = href.match(/\\/genre\\/([^\\/]+)\\//);
        if (m && m[1] !== 'noise-rock') {
            links.push({slug: m[1], text: text, href: href});
        }
    }
    
    // 找页面上显示"Noise Rock is a subgenre of X"的文字
    const bodyText = document.body.innerText;
    const lines = bodyText.split('\\n');
    const parentLines = [];
    for (let line of lines) {
        if (line.includes('subgenre') || line.includes('Subgenre') || line.includes('parent') || line.includes('Parent')) {
            parentLines.push(line);
        }
    }
    
    return {links: links.slice(0, 20), parentLines: parentLines};
}
""")

print(f"  找到 {len(result['links'])} 个其他流派链接", flush=True)
print(f"  父流派相关文字: {result['parentLines']}", flush=True)

if result['links']:
    print("  前10个链接:", flush=True)
    for link in result['links'][:10]:
        print(f"    {link['href']} -> {link['text']}", flush=True)

# 方法2: 直接看页面文本的前 100 行
print("\n[4] 看页面前 80 行文本...", flush=True)
text = page.evaluate("() => document.body.innerText")
lines = text.split('\n')
with open(r'C:\Users\qujt\.qclaw\workspace\_noise_rock_text.txt', 'w', encoding='utf-8') as f:
    for i, line in enumerate(lines[:80]):
        f.write(f"{i}: {line}\n")
print("  已保存: _noise_rock_text.txt", flush=True)

browser.close()
print("\n完成", flush=True)
