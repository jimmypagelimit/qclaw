#!/usr/bin/env python3
"""全局搜索所有涉及 cnt 的查询"""
import re

fpath = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\dist\server.js'
with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# 搜索所有 SELECT ... cnt ... 的查询
print("=== 所有涉及 cnt 的查询 ===")
for m in re.finditer(r'cnt', content):
    start = max(0, m.start()-100)
    end = min(len(content), m.end()+100)
    snippet = repr(content[start:end])
    if any(k in snippet for k in ['SELECT', 'as cnt', 'ORDER BY', 'WHERE', 'JOIN']):
        print(f"位置 {m.start()}:")
        print(snippet)
        print()
