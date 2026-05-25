#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tizzy Bac - 告密的心 收听数 +1
更新 albums 总表和 albums_2026 表
"""
import sqlite3
import os

db_path = r'G:\原创计划\music'
lines = []

lines.append('=== Tizzy Bac - 告密的心 收听数 +1 ===')
lines.append('')

# 连接数据库
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 1. 更新 albums 总表
lines.append('1. 更新 albums 总表...')
c.execute("SELECT album_id, total_listen_count FROM albums WHERE album_name LIKE '%告密的心%' AND artist LIKE '%Tizzy Bac%'")
result = c.fetchone()
if result:
    album_id = result[0]
    old_tc = result[1]
    new_tc = old_tc + 1
    lines.append(f'  找到: id={album_id}, tc={old_tc} → {new_tc}')
    c.execute("UPDATE albums SET total_listen_count = ? WHERE album_id = ?", (new_tc, album_id))
    lines.append(f'  ✓ 已更新 albums 总表')
else:
    lines.append('  ✗ 未找到专辑（异常）')

lines.append('')

# 2. 更新 albums_2026 表
lines.append('2. 更新 albums_2026 表...')
c.execute("SELECT album_id, total_listen_count FROM albums_2026 WHERE album_name LIKE '%告密的心%' AND artist LIKE '%Tizzy Bac%'")
result = c.fetchone()
if result:
    album_id_2026 = result[0]
    old_tc_2026 = result[1]
    new_tc_2026 = old_tc_2026 + 1
    lines.append(f'  找到: id={album_id_2026}, tc={old_tc_2026} → {new_tc_2026}')
    c.execute("UPDATE albums_2026 SET total_listen_count = ? WHERE album_id = ?", (new_tc_2026, album_id_2026))
    lines.append(f'  ✓ 已更新 albums_2026 表')
else:
    lines.append('  ✗ 未找到专辑（可能未添加到 2026 表）')

lines.append('')

# 提交
lines.append('=== 提交 ===')
conn.commit()
lines.append('✓ 已提交到数据库')
lines.append('')

# 验证
lines.append('=== 验证更新结果 ===')
c.execute("SELECT total_listen_count FROM albums WHERE album_name LIKE '%告密的心%' AND artist LIKE '%Tizzy Bac%'")
result = c.fetchone()
if result:
    lines.append(f'albums 总表: tc={result[0]}')

c.execute("SELECT total_listen_count FROM albums_2026 WHERE album_name LIKE '%告密的心%' AND artist LIKE '%Tizzy Bac%'")
result = c.fetchone()
if result:
    lines.append(f'albums_2026 表: tc={result[0]}')

conn.close()

output = '\n'.join(lines)

with open(r'C:\Users\qujt\.qclaw\workspace\update_tizzy_tc.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print('Done, saved to update_tizzy_tc.txt')
