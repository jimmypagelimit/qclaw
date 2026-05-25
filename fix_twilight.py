#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 The Twilight Sad - It's the Long Goodbye 的 tc 字段
从 '2026-03' 改为 1，并添加 RYM 评分 3.49
"""
import sqlite3
import os

db_path = r'G:\原创计划\music'
lines = []

lines.append('=== 修复 The Twilight Sad - It\'s the Long Goodbye ===')
lines.append('')

# 连接数据库
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 1. 检查当前 tc 值
lines.append('1. 检查当前 tc 值...')
c.execute("SELECT total_listen_count FROM albums WHERE album_id = 513")
tc_value = c.fetchone()[0]
lines.append(f'  albums 总表 tc 当前值: {tc_value} (类型: {type(tc_value).__name__})')

c.execute("SELECT total_listen_count FROM albums_2026 WHERE album_id = 114")
tc_value_2026 = c.fetchone()[0]
lines.append(f'  albums_2026 表 tc 当前值: {tc_value_2026} (类型: {type(tc_value_2026).__name__})')
lines.append('')

# 2. 修正 tc 值并更新 RYM 评分
lines.append('2. 修正 tc 值并更新 RYM 评分...')

# albums 总表：tc 改为 1（首次收听），添加 RYM 3.49
new_tc = 1
new_rating = 3.49
c.execute("UPDATE albums SET total_listen_count = ?, rating = ? WHERE album_id = 513", 
          (new_tc, new_rating))
lines.append(f'  ✓ albums 总表: tc={new_tc}, rating={new_rating}')

# albums_2026 表：tc 改为 1（首次收听），添加 RYM 3.49
c.execute("UPDATE albums_2026 SET total_listen_count = ?, rating = ? WHERE album_id = 114", 
          (new_tc, new_rating))
lines.append(f'  ✓ albums_2026 表: tc={new_tc}, rating={new_rating}')
lines.append('')

# 3. 提交数据库
lines.append('3. 提交数据库...')
conn.commit()
lines.append('  ✓ 提交成功')
lines.append('')

# 4. 验证更新结果
lines.append('4. 验证更新结果...')
c.execute("SELECT album_name, artist, total_listen_count, rating FROM albums WHERE album_id = 513")
result = c.fetchone()
lines.append(f'  albums 总表: name={result[0]}, artist={result[1]}, tc={result[2]}, RYM={result[3]}')

c.execute("SELECT album_name, artist, total_listen_count, rating FROM albums_2026 WHERE album_id = 114")
result = c.fetchone()
lines.append(f'  albums_2026 表: name={result[0]}, artist={result[1]}, tc={result[2]}, RYM={result[3]}')
lines.append('')

# 5. 检查封面文件
lines.append('5. 检查封面文件...')
cover1 = r'G:\原创计划\covers\513-The_Twilight_Sad-It_s_the_Long_Goodbye.jpg'
cover2 = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\covers\114-The_Twilight_Sad-It_s_the_Long_Goodbye.jpg'
lines.append(f'  封面1: {cover1}')
lines.append(f'  存在: {os.path.exists(cover1)}')
if os.path.exists(cover1):
    lines.append(f'  大小: {os.path.getsize(cover1)} bytes')
lines.append(f'  封面2: {cover2}')
lines.append(f'  存在: {os.path.exists(cover2)}')
if os.path.exists(cover2):
    lines.append(f'  大小: {os.path.getsize(cover2)} bytes')
lines.append('')

conn.close()

lines.append('=== 修复完成 ===')
lines.append('下一步：下载封面（如不存在）')

output = '\n'.join(lines)

with open(r'C:\Users\qujt\.qclaw\workspace\fix_twilight_result.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print('Done, saved to fix_twilight_result.txt')
