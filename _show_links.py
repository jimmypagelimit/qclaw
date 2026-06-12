#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""展示 rym_user_info.json 中的链接"""
import json

with open("rym_user_info.json", encoding="utf-8") as f:
    data = json.load(f)

links = data["all_links"]
print(f"共 {len(links)} 个链接\n")

# 按关键词分类
for i, l in enumerate(links):
    text = l["text"][:60]
    href = l["href"][:100]
    print(f"[{i:3d}] {text:60s} -> {href}")

print("\n\n=== 特殊关键词 ===")
keywords = ["profile", "account", "setting", "logout", "sign", "hello", "hi ", "welcome", "my ", "user", "login"]
for i, l in enumerate(links):
    text_lower = l["text"].lower()
    for kw in keywords:
        if kw in text_lower:
            print(f"[{i:3d}] {l['text'][:60]:60s} -> {l['href'][:100]}")
            break

print(f"\n\nUsernames: {data.get('usernames', [])}")
print(f"Greeting: {data.get('greeting')}")
print(f"Keywords: {data.get('keywords', [])}")
print(f"RYM cookies: {data.get('rym_cookies', {})}")
