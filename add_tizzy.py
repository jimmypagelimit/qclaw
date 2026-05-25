#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加 Tizzy Bac - 告密的心 (The Tell-Tale Heart) 到数据库
"""
import sqlite3
import os

db_path = r'G:\原创计划\music'
lines = []

lines.append('=== 新增专辑：告密的心 (The Tell-Tale Heart) ===')
lines.append('')

# 连接数据库
conn = sqlite3.connect(db_path)
c = conn.cursor()

# 获取 albums 总表下一个 ID
c.execute("SELECT MAX(album_id) FROM albums")
max_id_albums = c.fetchone()[0]
new_id_albums = max_id_albums + 1 if max_id_albums else 1
lines.append(f'albums 总表当前最大 ID: {max_id_albums}')
lines.append(f'新专辑 ID: {new_id_albums}')
lines.append('')

# 获取 albums_2026 表下一个 ID
c.execute("SELECT MAX(album_id) FROM albums_2026")
max_id_2026 = c.fetchone()[0]
new_id_2026 = max_id_2026 + 1 if max_id_2026 else 1
lines.append(f'albums_2026 表当前最大 ID: {max_id_2026}')
lines.append(f'新专辑在 2026 表的 ID: {new_id_2026}')
lines.append('')

# 插入 albums 总表
lines.append('1. 插入 albums 总表...')
c.execute("""
    INSERT INTO albums (
        album_id, album_name, artist, country, region, genre, rating, description,
        is_compilation, first_listen_date, total_listen_count, release_company,
        cover_image_url, duration, composition_score, lyrics_score, arrangement_score,
        performance_score, overall_score, release_year, style, producer
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    new_id_albums,
    '告密的心 (The Tell-Tale Heart)',
    'Tizzy Bac',
    None,  # country
    None,  # region
    'Indie Rock, Piano Rock',
    '3.14',  # RYM 评分
    None,  # description
    0,  # is_compilation
    '2026-05',  # first_listen_date (假设今年首次听)
    1,  # total_listen_count (听 1 次)
    None,  # release_company
    f'covers/{new_id_albums}-Tizzy_Bac-告密的心_The_Tell-Tale_Heart.jpg',
    None,  # duration
    None,  # composition_score
    None,  # lyrics_score
    None,  # arrangement_score
    None,  # performance_score
    None,  # overall_score (用户未评分)
    2011,  # release_year
    None,  # style
    None   # producer
))
lines.append(f'  ✓ 已插入 albums 总表 (id={new_id_albums})')

# 插入 albums_2026 表
lines.append('')
lines.append('2. 插入 albums_2026 表...')
c.execute("""
    INSERT INTO albums_2026 (
        album_id, album_name, artist, country, region, genre, rating, description,
        is_compilation, first_listen_date, total_listen_count, release_company,
        cover_image_url, duration, composition_score, lyrics_score, arrangement_score,
        performance_score, overall_score, release_year, style, producer
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    new_id_2026,
    '告密的心 (The Tell-Tale Heart)',
    'Tizzy Bac',
    None,
    None,
    'Indie Rock, Piano Rock',
    '3.14',
    None,
    0,
    '2026-05',
    1,
    None,
    f'covers/{new_id_2026}-Tizzy_Bac-告密的心_The_Tell-Tale_Heart.jpg',
    None,
    None,
    None,
    None,
    None,
    None,
    2011,
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
c.execute("SELECT * FROM albums WHERE album_id = ?", (new_id_albums,))
result = c.fetchone()
if result:
    lines.append(f'albums 总表: id={result[0]} | {result[1]} | tc={result[9]} | RYM={result[6]} | score={result[17]}')

c.execute("SELECT * FROM albums_2026 WHERE album_id = ?", (new_id_2026,))
result = c.fetchone()
if result:
    lines.append(f'albums_2026 表: id={result[0]} | {result[1]} | tc={result[9]} | RYM={result[6]} | score={result[17]}')

lines.append('')
lines.append('=== 下一步 ===')
lines.append(f'1. 下载封面到: covers/{new_id_albums}-Tizzy_Bac-告密的心_The_Tell-Tale_Heart.jpg')
lines.append(f'2. 同时下载到: covers/{new_id_2026}-Tizzy_Bac-告密的心_The_Tell-Tale_Heart.jpg')
lines.append('3. 重启 Web 服务')

conn.close()

output = '\n'.join(lines)

with open(r'C:\Users\qujt\.qclaw\workspace\add_tizzy_result.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print('Done, saved to add_tizzy_result.txt')
