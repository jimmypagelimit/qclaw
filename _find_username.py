#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""找出 RYM 当前登录用户名 - 输出到文件"""

import json, sys, time
from cloakbrowser import launch

COOKIE_FILE = r"C:\Users\qujt\.qclaw\workspace\tasks\rym-expert\data\rym_cookies.json"

with open(COOKIE_FILE, encoding="utf-8") as f:
    storage = json.load(f)

browser = launch(headless=False)
context = browser.new_context(storage_state=storage)
page = context.new_page()

page.goto("https://rateyourmusic.com/", timeout=90000)
time.sleep(20)

result = page.evaluate("""() => {
    let info = {};

    // 1. 所有 a 标签
    let links = [];
    for (let a of document.querySelectorAll('a')) {
        if (a.href && a.innerText.trim()) {
            links.push({text: a.innerText.trim().slice(0, 80), href: a.href.slice(0, 120)});
        }
    }
    info['all_links'] = links;

    // 2. 找关键词元素
    let keywords = [];
    let keywordsList = ['my profile', 'my lists', 'my ratings', 'account', 'profile', 'lists',
        'sign out', 'logout', 'settings'];
    for (let el of document.querySelectorAll('*')) {
        let t = (el.innerText || '').trim().toLowerCase();
        for (let kw of keywordsList) {
            if (t === kw) {
                keywords.push({text: el.innerText.trim(), tag: el.tagName, id: el.id, class: el.className.slice(0, 50)});
            }
        }
    }
    info['keywords'] = keywords;

    // 3. Head 中的 meta/script
    let headData = [];
    for (let s of document.querySelectorAll('script')) {
        let src = s.src || '';
        if (src.includes('sonemic') || src.includes('rym')) {
            headData.push({src: src.slice(0, 100)});
        }
    }
    info['head_scripts'] = headData;

    // 4. body 文本中找 "Hello" "Hi" "Welcome"
    let bodyText = document.body ? document.body.innerText : '';
    let greeting = bodyText.match(/[Hh](?:ello|i|ey)[^\\n]{0,100}/);
    info['greeting'] = greeting ? greeting[0] : null;

    // 5. 找 /~username 格式链接
    let usernames = [];
    let userRegex = /~([a-zA-Z0-9_-]+)/g;
    for (let a of document.querySelectorAll('a')) {
        if (a.href) {
            let m = a.href.match(/~([a-zA-Z0-9_-]+)/);
            if (m && !['logout','log-in','sign-up','settings','register'].includes(m[1])) {
                if (!usernames.includes(m[1])) {
                    usernames.push(m[1]);
                }
            }
        }
    }
    info['usernames'] = usernames;

    // 6. RYM 相关 cookie
    let rymCookies = {};
    document.cookie.split('; ').forEach(c => {
        let parts = c.split('=');
        let key = parts[0];
        if (key.toLowerCase().includes('user') || key.toLowerCase().includes('rym')) {
            rymCookies[key] = parts.slice(1).join('=');
        }
    });
    info['rym_cookies'] = rymCookies;

    return info;
}""")

# 写文件
with open("rym_user_info.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"已保存: rym_user_info.json")
print(f"  links: {len(result.get('all_links', []))}")
print(f"  keywords: {result.get('keywords', [])}")
print(f"  greeting: {result.get('greeting')}")
print(f"  usernames: {result.get('usernames', [])}")
print(f"  rym_cookies: {result.get('rym_cookies', {})}")

browser.close()
