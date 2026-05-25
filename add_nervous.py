#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加 Car Seat Headrest - Nervous Young Man 到 albums_2026 表
（albums 总表已有此专辑，id=383）
"""
import sqlite3
import os

db_path = r'G:\原创计划\music'
lines = []

lines.append('=== 新增专辑到 2026 表：Nervous Young Man ===')
lines.append('')

# 连接数据库
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 检查 albums 总表现有记录
lines.append('1. 检查 albums 总表现有记录...')
c.execute("SELECT * FROM albums WHERE album_name LIKE '%Nervous Young Man%' AND artist LIKE '%Car Seat Headrest%'")
result = c.fetchone()
if result:
    lines.append(f'  ✓ 找到记录: id={result[0]}, tc={result[10]}, first_listen={result[9]}')
    lines.append(f'  需要更新: total_listen_count {result[10]} → {result[10] + 1}')
    albums_id = result[0]
    current_tc = result[10]
else:
    lines.append('  ✗ 未找到（异常，应该存在）')
    conn.close()
    sys.exit(1)

lines.append('')

# 获取 albums_2026 表下一个 ID
c.execute("SELECT MAX(album_id) FROM albums_2026")
max_id_2026 = c.fetchone()[0]
new_id_2026 = max_id_2026 + 1 if max_id_2026 else 1
lines.append(f'albums_2026 表当前最大 ID: {max_id_2026}')
lines.append(f'新专辑在 2026 表的 ID: {new_id_2026}')
lines.append('')

# 插入 albums_2026 表
lines.append('2. 插入 albums_2026 表...')
c.execute("""
    INSERT INTO albums_2026 (
        album_id, album_name, artist, country, region, genre, rating, description,
        is_compilation, first_listen_date, total_listen_count, release_company,
        cover_image_url, duration, composition_score, lyrics_meaning_score,
        creativity_score, arrangement_score, vocal_performance_score,
        instrumental_performance_score, sincerity_score, subjective_score,
        overall_score, release_year, style, producer
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    new_id_2026,
    'Nervous Young Man',
    'Car Seat Headrest',
    None,
    None,
    'Slacker Rock, Singer-Songwriter',
    3.85,  # RYM 评分
    None,
    0,
    '2026-05',  # 首次在 2026 年听
    1,  # total_listen_count (2026 年听 1 次)
    None,
    f'covers/{new_id_2026}-Car_Seat_Headrest-Nervous_Young_Man.jpg',
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    '2013-08-23',  # release_year (TEXT 类型)
    None,
    None
))
lines.append(f'  ✓ 已插入 albums_2026 表 (id={new_id_2026})')

# 更新 albums 总表的 total_listen_count
lines.append('')
lines.append('3. 更新 albums 总表 total_listen_count...')
new_tc = current_tc + 1
c.execute("UPDATE albums SET total_listen_count = ? WHERE album_id = ?", (new_tc, albums_id))
lines.append(f'  ✓ 已更新: {current_tc} → {new_tc}')

# 提交
lines.append('')
lines.append('=== 提交 ===')
conn.commit()
lines.append('✓ 已提交到数据库')
lines.append('')

# 验证
lines.append('=== 验证插入结果 ===')
c.execute("SELECT * FROM albums_2026 WHERE album_id = ?", (new_id_2026,))
result = c.fetchone()
if result:
    lines.append(f'albums_2026 表: id={result[0]} | {result[1]} | tc={result[10]} | RYM={result[6]}')

c.execute("SELECT total_listen_count FROM albums WHERE album_id = ?", (albums_id,))
result = c.fetchone()
if result:
    lines.append(f'albums 总表: tc={result[0]}')

lines.append('')
lines.append('=== 下一步 ===')
lines.append(f'1. 下载封面到: covers/{new_id_2026}-Car_Seat_Headrest-Nervous_Young_Man.jpg')
lines.append('2. 重启 Web 服务')

conn.close()

output = '\n'.join(lines)

with open(r'C:\Users\qujt\.qclaw\workspace\add_nervous_result.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print('Done, saved to add_nervous_result.txt')
