#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 albums 和 albums_2026 表结构
"""
import sqlite3
import os

db_path = r'G:\原创计划\music'
lines = []

lines.append('=== 检查表结构 ===')
lines.append('')

if not os.path.exists(db_path):
    lines.append(f'✗ 数据库文件不存在: {db_path}')
else:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # 检查 albums 表结构
    lines.append('1. albums 表结构：')
    c.execute("PRAGMA table_info(albums)")
    columns = c.fetchall()
    for col in columns:
        lines.append(f'  {col[0]:2d} {col[1]:30s} {col[2]:15s} {"NOT NULL" if col[3] else "NULL":10s} {"DEFAULT "+str(col[4]) if col[4] else "":15s} {"PK" if col[5] else "":5s}')
    lines.append('')
    
    # 检查 albums_2026 表结构
    lines.append('2. albums_2026 表结构：')
    c.execute("PRAGMA table_info(albums_2026)")
    columns = c.fetchall()
    for col in columns:
        lines.append(f'  {col[0]:2d} {col[1]:30s} {col[2]:15s} {"NOT NULL" if col[3] else "NULL":10s} {"DEFAULT "+str(col[4]) if col[4] else "":15s} {"PK" if col[5] else "":5s}')
    lines.append('')
    
    # 找一个现有记录看看
    lines.append('3. 现有记录示例 (albums 表第一条):')
    c.execute("SELECT * FROM albums LIMIT 1")
    row = c.fetchone()
    if row:
        # 获取列名
        c.execute("PRAGMA table_info(albums)")
        col_names = [col[1] for col in c.fetchall()]
        for i, (col_name, value) in enumerate(zip(col_names, row)):
            lines.append(f'  {col_name} = {value}')
    
    conn.close()

output = '\n'.join(lines)

with open(r'C:\Users\qujt\.qclaw\workspace\check_schema2.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print('Done, saved to check_schema2.txt')
