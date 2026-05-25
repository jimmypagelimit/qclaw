#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一张悬专辑：更新 albums_2026 表的 cover_image_url 和 artist 字段
"""
import sqlite3
import os

db = r'G:\原创计划\music'
if os.path.isdir(db):
    db = os.path.join(db, 'music')

conn = sqlite3.connect(db)
c = conn.cursor()

lines = []

lines.append('=== 开始更新 albums_2026 表 ===')
lines.append('')

# 1. 更新 id=39 (城市)
lines.append('1. 更新 id=39 (城市):')
lines.append('   - cover_image_url: covers/448-張懸_[Deserts_Chang]-城市.jpg')
lines.append('   - 更新为: covers/168-张悬-城市.jpg')
c.execute("UPDATE albums_2026 SET cover_image_url = 'covers/168-张悬-城市.jpg' WHERE album_id = 39")
lines.append('   OK 已更新 cover_image_url')
lines.append('   - artist: 张悬 [Deserts Chang]')
lines.append('   - 更新为: 张悬')
c.execute("UPDATE albums_2026 SET artist = '张悬' WHERE album_id = 39")
lines.append('   OK 已更新 artist')
lines.append('')

# 2. 更新 id=40 (神的游戏)
lines.append('2. 更新 id=40 (神的游戏):')
lines.append('   - cover_image_url: covers/449-張懸_[Deserts_Chang]-神的遊戲_Games_We_Play.jpg')
lines.append('   - 更新为: covers/6-张悬-神的游戏.jpg')
c.execute("UPDATE albums_2026 SET cover_image_url = 'covers/6-张悬-神的游戏.jpg' WHERE album_id = 40")
lines.append('   OK 已更新 cover_image_url')
lines.append('   - artist: 张悬 [Deserts Chang]')
lines.append('   - 更新为: 张悬')
c.execute("UPDATE albums_2026 SET artist = '张悬' WHERE album_id = 40")
lines.append('   OK 已更新 artist')
lines.append('')

# 提交更改
conn.commit()
lines.append('=== 更新完成，已提交到数据库 ===')
lines.append('')

# 验证更新结果
lines.append('=== 验证更新结果 ===')
c.execute("SELECT album_id, album_name, artist, cover_image_url FROM albums_2026 WHERE album_id IN (39, 40)")
rows = c.fetchall()
for r in rows:
    lines.append(f'  id={r[0]} | {r[1]}')
    lines.append(f'    artist={r[2]}')
    lines.append(f'    cover={r[3]}')
lines.append('')

conn.close()

# 3. 删除繁体封面文件
lines.append('=== 删除繁体封面文件 ===')
covers_dir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\covers'
files_to_delete = [
    '448-張懸_[Deserts_Chang]-城市.jpg',
    '449-張懸_[Deserts_Chang]-神的遊戲_Games_We_Play.jpg'
]
for fname in files_to_delete:
    fpath = os.path.join(covers_dir, fname)
    if os.path.exists(fpath):
        os.remove(fpath)
        lines.append(f'  OK 已删除: {fname}')
    else:
        lines.append(f'  SKIP 不存在: {fname}')
lines.append('')

output = '\n'.join(lines)

# 只写文件，不打印到控制台
with open(r'C:\Users\qujt\.qclaw\workspace\zx_unified.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print('Done, saved to zx_unified.txt')
