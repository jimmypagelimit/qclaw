#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新增苏紫旭 & The Paramecia - 悲歌欢唱 Lamenting in Delight (2026-05-15)
入库到 albums 总表 + albums_2026 表
"""
import sqlite3
import os

db = r'G:\原创计划\music'
if os.path.isdir(db):
    db = os.path.join(db, 'music')

conn = sqlite3.connect(db)
c = conn.cursor()

lines = []

lines.append('=== 新增专辑：悲歌欢唱 Lamenting in Delight ===')
lines.append('')

# 检查 albums 总表当前最大 ID
c.execute("SELECT MAX(album_id) FROM albums")
max_id = c.fetchone()[0]
new_id = max_id + 1
lines.append(f'albums 总表当前最大 ID: {max_id}')
lines.append(f'新专辑 ID: {new_id}')
lines.append('')

# 插入 albums 总表（根据实际字段，去掉 language）
sql_albums = """INSERT INTO albums 
                  (album_id, album_name, artist, release_year, first_listen_date, 
                   total_listen_count, rating, overall_score, genre, cover_image_url)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
values_albums = (
    new_id,
    '悲歌欢唱 Lamenting in Delight',
    '苏紫旭 & The Paramecia',
    '2026',  # release_year
    '2026-05',  # first_listen_date
    4,  # total_listen_count
    3.50,  # rating (RYM 3.50)
    None,  # overall_score (暂未评分)
    'Folk Rock, Progressive Rock, Indie Folk',
    f'covers/{new_id}-苏紫旭_&_The_Paramecia-悲歌欢唱_Lamenting_in_Delight.jpg'
)
c.execute(sql_albums, values_albums)
lines.append(f'✓ 已插入 albums 总表 (id={new_id})')
lines.append('')

# 检查 albums_2026 表当前最大 ID
c.execute("SELECT MAX(album_id) FROM albums_2026")
max_id_2026 = c.fetchone()[0]
new_id_2026 = (max_id_2026 or 0) + 1
lines.append(f'albums_2026 表当前最大 ID: {max_id_2026}')
lines.append(f'新专辑在 2026 表的 ID: {new_id_2026}')
lines.append('')

# 插入 albums_2026 表
sql_2026 = """INSERT INTO albums_2026
                (album_id, album_name, artist, release_year, first_listen_date,
                 total_listen_count, rating, overall_score, genre, cover_image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
values_2026 = (
    new_id_2026,
    '悲歌欢唱 Lamenting in Delight',
    '苏紫旭 & The Paramecia',
    '2026',
    '2026-05',
    4,
    3.50,
    None,
    'Folk Rock, Progressive Rock, Indie Folk',
    f'covers/{new_id_2026}-苏紫旭_&_The_Paramecia-悲歌欢唱_Lamenting_in_Delight.jpg'
)
c.execute(sql_2026, values_2026)
lines.append(f'✓ 已插入 albums_2026 表 (id={new_id_2026})')
lines.append('')

# 提交
conn.commit()
lines.append('=== 提交成功 ===')
lines.append('')

# 验证
lines.append('=== 验证插入结果 ===')
c.execute("SELECT album_id, album_name, artist, total_listen_count, rating, overall_score FROM albums WHERE album_id = ?", (new_id,))
r = c.fetchone()
lines.append(f'albums 总表: id={r[0]} | {r[1]} | tc={r[3]} | RYM={r[4]} | score={r[5]}')

c.execute("SELECT album_id, album_name, artist, total_listen_count, rating, overall_score FROM albums_2026 WHERE album_id = ?", (new_id_2026,))
r2 = c.fetchone()
if r2:
    lines.append(f'albums_2026 表: id={r2[0]} | {r2[1]} | tc={r2[3]} | RYM={r2[4]} | score={r2[5]}')
lines.append('')

conn.close()

lines.append('=== 下一步 ===')
lines.append(f'1. 下载封面到: covers/{new_id}-苏紫旭_&_The_Paramecia-悲歌欢唱_Lamenting_in_Delight.jpg')
lines.append(f'2. 同时下载到: covers/{new_id_2026}-苏紫旭_&_The_Paramecia-悲歌欢唱_Lamenting_in_Delight.jpg')
lines.append('3. 重启 Web 服务')

output = '\n'.join(lines)

with open(r'C:\Users\qujt\.qclaw\workspace\add_szx_result.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print('Done, saved to add_szx_result.txt')
