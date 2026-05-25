#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加 Maria BC - Marathon 到数据库
"""
import sqlite3
import os

db_path = r'G:\原创计划\music'
lines = []

lines.append('=== 新增专辑：Maria BC - Marathon ===')
lines.append('')

# 连接数据库
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 获取 albums 总表下一个 ID
c.execute("SELECT MAX(album_id) FROM albums")
max_id = c.fetchone()[0]
new_id = max_id + 1 if max_id else 1
lines.append(f'albums 总表当前最大 ID: {max_id}')
lines.append(f'新专辑在总表的 ID: {new_id}')
lines.append('')

# 插入 albums 总表
lines.append('1. 插入 albums 总表...')
c.execute("""
    INSERT INTO albums (
        album_id, album_name, artist, country, region, genre, rating, description,
        is_compilation, first_listen_date, total_listen_count, release_company,
        cover_image_url, duration, composition_score, lyrics_meaning_score,
        creativity_score, arrangement_score, vocal_performance_score,
        instrumental_performance_score, sincerity_score, subjective_score,
        overall_score, release_year, style, producer
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    new_id,
    'Marathon',
    'Maria BC',
    None,
    None,
    'Indie Folk, Singer-Songwriter, Psychedelic Folk',
    3.47,  # RYM 评分
    None,
    0,
    '2026-05',  # 首次听歌时间
    3,  # total_listen_count (听 3 次)
    None,
    f'covers/{new_id}-Maria_BC-Marathon.jpg',
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
    '2026-02-27',  # release_year (TEXT 类型)
    None,
    None
))
lines.append(f'  ✓ 已插入 albums 总表 (id={new_id})')

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
    'Marathon',
    'Maria BC',
    None,
    None,
    'Indie Folk, Singer-Songwriter, Psychedelic Folk',
    3.47,  # RYM 评分
    None,
    0,
    '2026-05',  # 首次在 2026 年听
    3,  # total_listen_count (2026 年听 3 次)
    None,
    f'covers/{new_id_2026}-Maria_BC-Marathon.jpg',
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
    '2026-02-27',  # release_year (TEXT 类型)
    None,
    None
))
lines.append(f'  ✓ 已插入 albums_2026 表 (id={new_id_2026})')

# 提交
lines.append('')
lines.append('=== 提交 ===')
conn.commit()
lines.append('✓ 已提交到数据库')
lines.append('')

# 验证
lines.append('=== 验证插入结果 ===')
c.execute("SELECT * FROM albums WHERE album_id = ?", (new_id,))
result = c.fetchone()
if result:
    lines.append(f'albums 总表: id={result[0]} | {result[1]} | tc={result[10]} | RYM={result[6]}')

c.execute("SELECT * FROM albums_2026 WHERE album_id = ?", (new_id_2026,))
result = c.fetchone()
if result:
    lines.append(f'albums_2026 表: id={result[0]} | {result[1]} | tc={result[10]} | RYM={result[6]}')

lines.append('')
lines.append('=== 下一步 ===')
lines.append(f'1. 下载封面到: covers/{new_id}-Maria_BC-Marathon.jpg 和 covers/{new_id_2026}-Maria_BC-Marathon.jpg')
lines.append('2. 重启 Web 服务')

conn.close()

output = '\n'.join(lines)

with open(r'C:\Users\qujt\.qclaw\workspace\add_maria_result.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print('Done, saved to add_maria_result.txt')
