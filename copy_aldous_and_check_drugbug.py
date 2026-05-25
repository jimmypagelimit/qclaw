#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
复制 Aldous Harding 封面到第二个位置
然后检查 drug bug - Hell for a Basement
"""
import sqlite3
import os
import shutil

db_path = r'G:\原创计划\music'
lines = []

lines.append('=== 复制封面 + 检查 drug bug ===')
lines.append('')

# 1. 复制 Aldous Harding 封面
lines.append('1. 复制 Aldous Harding 封面...')
cover_dir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\covers'
cover1 = os.path.join(cover_dir, '521-Aldous_Harding-Train_on_the_Island.jpg')
cover2 = os.path.join(cover_dir, '122-Aldous_Harding-Train_on_the_Island.jpg')

if os.path.exists(cover1):
    shutil.copy2(cover1, cover2)
    lines.append(f'  ✓ 已复制: {os.path.basename(cover2)} ({os.path.getsize(cover2)} bytes)')
else:
    lines.append(f'  ✗ 源文件不存在: {cover1}')

lines.append('')

# 2. 检查 drug bug - Hell for a Basement
lines.append('2. 检查 drug bug - Hell for a Basement...')
lines.append('')

if not os.path.exists(db_path):
    lines.append(f'✗ 数据库文件不存在: {db_path}')
else:
    # 连接数据库
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # 检查 albums 总表
    lines.append('  albums 总表检查...')
    c.execute("SELECT * FROM albums WHERE album_name LIKE '%Hell for a Basement%' AND artist LIKE '%drug bug%'")
    results = c.fetchall()
    if results:
        lines.append(f'  找到 {len(results)} 条记录:')
        for row in results:
            lines.append(f'  - id={row[0]}, name={row[1]}, artist={row[2]}, tc={row[9]}, RYM={row[6]}')
        lines.append('  结论: 专辑已存在，需要更新 tc 和 RYM')
    else:
        lines.append('  ✗ 未找到（需要新增）')
        lines.append('  结论: 需要新增到两个表')
    
    lines.append('')
    
    # 检查 albums_2026 表
    lines.append('  albums_2026 表检查...')
    c.execute("SELECT * FROM albums_2026 WHERE album_name LIKE '%Hell for a Basement%' AND artist LIKE '%drug bug%'")
    results = c.fetchall()
    if results:
        lines.append(f'  找到 {len(results)} 条记录:')
        for row in results:
            lines.append(f'  - id={row[0]}, name={row[1]}, artist={row[2]}, tc={row[9]}, RYM={row[6]}')
    else:
        lines.append('  ✗ 未找到（需要新增）')
    
    lines.append('')
    
    # 检查 drug bug 的所有专辑
    lines.append('  drug bug 所有专辑检查...')
    c.execute("SELECT * FROM albums WHERE artist LIKE '%drug bug%'")
    results = c.fetchall()
    if results:
        lines.append(f'  找到 {len(results)} 条 drug bug 专辑:')
        for row in results:
            lines.append(f'  - id={row[0]}, name={row[1]}, tc={row[9]}, RYM={row[6]}')
    else:
        lines.append('  ✗ 未找到 drug bug 的专辑')
    
    conn.close()

lines.append('')
lines.append('=== 结论 ===')
lines.append('根据检查结果决定下一步操作。')

output = '\n'.join(lines)

with open(r'C:\Users\qujt\.qclaw\workspace\copy_aldous_and_check_drugbug.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print('Done, saved to copy_aldous_and_check_drugbug.txt')
