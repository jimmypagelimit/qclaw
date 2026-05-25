#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 Asher White - Jessica Pratt 的收听次数和 RYM 评分
"""
import sqlite3
import os

db_path = r'G:\原创计划\music'
lines = []

lines.append('=== 更新 Asher White - Jessica Pratt ===')
lines.append('')

# 连接数据库
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 1. 检查当前值
lines.append('1. 检查当前值...')
c.execute("SELECT total_listen_count, rating FROM albums WHERE album_id = 434")
result = c.fetchone()
if result:
    current_tc = result[0]
    current_rating = result[1]
    lines.append(f'  albums 总表: tc={current_tc}, RYM={current_rating}')
else:
    lines.append('  ✗ 未找到专辑（异常）')

c.execute("SELECT total_listen_count, rating FROM albums_2026 WHERE album_id = 25")
result = c.fetchone()
if result:
    current_tc_2026 = result[0]
    current_rating_2026 = result[1]
    lines.append(f'  albums_2026 表: tc={current_tc_2026}, RYM={current_rating_2026}')
else:
    lines.append('  ✗ 未找到专辑（异常）')

lines.append('')

# 2. 更新 albums 总表
lines.append('2. 更新 albums 总表...')
new_tc = current_tc + 1 if current_tc else 1
lines.append(f'  tc: {current_tc} → {new_tc}')
lines.append(f'  RYM: {current_rating} → 3.36')
c.execute("UPDATE albums SET total_listen_count = ?, rating = ? WHERE album_id = ?", 
          (new_tc, 3.36, 434))
lines.append('  ✓ 已更新 albums 总表')

lines.append('')

# 3. 更新 albums_2026 表
lines.append('3. 更新 albums_2026 表...')
new_tc_2026 = current_tc_2026 + 1 if current_tc_2026 else 1
lines.append(f'  tc: {current_tc_2026} → {new_tc_2026}')
lines.append(f'  RYM: {current_rating_2026} → 3.36')
c.execute("UPDATE albums_2026 SET total_listen_count = ?, rating = ? WHERE album_id = ?", 
          (new_tc_2026, 3.36, 25))
lines.append('  ✓ 已更新 albums_2026 表')

# 提交
lines.append('')
lines.append('=== 提交 ===')
conn.commit()
lines.append('✓ 已提交到数据库')
lines.append('')

# 验证
lines.append('=== 验证更新结果 ===')
c.execute("SELECT total_listen_count, rating FROM albums WHERE album_id = 434")
result = c.fetchone()
if result:
    lines.append(f'albums 总表: tc={result[0]}, RYM={result[1]}')

c.execute("SELECT total_listen_count, rating FROM albums_2026 WHERE album_id = 25")
result = c.fetchone()
if result:
    lines.append(f'albums_2026 表: tc={result[0]}, RYM={result[1]}')

conn.close()

output = '\n'.join(lines)

with open(r'C:\Users\qujt\.qclaw\workspace\update_asher_result.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print('Done, saved to update_asher_result.txt')
