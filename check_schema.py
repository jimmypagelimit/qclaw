#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 albums 表的字段结构
"""
import sqlite3
import os

db = r'G:\原创计划\music'
if os.path.isdir(db):
    db = os.path.join(db, 'music')

conn = sqlite3.connect(db)
c = conn.cursor()

lines = []

lines.append('=== albums 表结构 ===')
c.execute("PRAGMA table_info(albums)")
columns = c.fetchall()
for col in columns:
    lines.append(f'  {col[1]:20s}  {col[2]}')

lines.append('')
lines.append('=== albums_2026 表结构 ===')
try:
    c.execute("PRAGMA table_info(albums_2026)")
    columns2 = c.fetchall()
    for col in columns2:
        lines.append(f'  {col[1]:20s}  {col[2]}')
except Exception as e:
    lines.append(f'Error: {e}')

conn.close()

output = '\n'.join(lines)

with open(r'C:\Users\qujt\.qclaw\workspace\check_schema.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print('Done, saved to check_schema.txt')
