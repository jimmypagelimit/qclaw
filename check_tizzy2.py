#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 Tizzy Bac - 如果看見地獄，我就不怕魔鬼 是否已在数据库中
"""
import sqlite3
import os

db_path = r'G:\原创计划\music'
lines = []

lines.append('=== 检查 Tizzy Bac - 如果看見地獄，我就不怕魔鬼 ===')
lines.append('')

# 检查 G 盘是否挂载
if not os.path.exists(db_path):
    lines.append(f'✗ 数据库文件不存在: {db_path}')
    lines.append('G 盘可能未挂载')
else:
    lines.append(f'✓ 数据库文件存在: {db_path}')
    lines.append('')
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # 检查 albums 总表
    lines.append('1. albums 总表检查...')
    c.execute("SELECT * FROM albums WHERE album_name LIKE '%如果看見地獄%' AND artist LIKE '%Tizzy Bac%'")
    results = c.fetchall()
    if results:
        lines.append(f'  找到 {len(results)} 条记录:')
        for row in results:
            lines.append(f'  - id={row[0]}, name={row[1]}, artist={row[2]}, tc={row[9]}, RYM={row[6]}')
    else:
        lines.append('  ✗ 未找到（需要新增）')
    
    lines.append('')
    
    # 检查 albums_2026 表
    lines.append('2. albums_2026 表检查...')
    c.execute("SELECT * FROM albums_2026 WHERE album_name LIKE '%如果看見地獄%' AND artist LIKE '%Tizzy Bac%'")
    results = c.fetchall()
    if results:
        lines.append(f'  找到 {len(results)} 条记录:')
        for row in results:
            lines.append(f'  - id={row[0]}, name={row[1]}, artist={row[2]}, tc={row[9]}, RYM={row[6]}')
    else:
        lines.append('  ✗ 未找到（需要新增）')
    
    lines.append('')
    
    # 检查 Tizzy Bac 的所有专辑
    lines.append('3. Tizzy Bac 所有专辑检查...')
    c.execute("SELECT * FROM albums WHERE artist LIKE '%Tizzy Bac%'")
    results = c.fetchall()
    if results:
        lines.append(f'  找到 {len(results)} 条 Tizzy Bac 专辑:')
        for row in results:
            lines.append(f'  - id={row[0]}, name={row[1]}, tc={row[9]}, RYM={row[6]}')
    else:
        lines.append('  ✗ 未找到 Tizzy Bac 的专辑')
    
    conn.close()

lines.append('')
lines.append('=== 结论 ===')
if not os.path.exists(db_path):
    lines.append('G 盘未挂载，无法操作数据库。')
else:
    lines.append('根据检查结果决定是否需要新增此专辑。')

output = '\n'.join(lines)

with open(r'C:\Users\qujt\.qclaw\workspace\check_tizzy2.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print('Done, saved to check_tizzy2.txt')
