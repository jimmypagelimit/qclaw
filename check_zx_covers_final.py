#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查张悬专辑的 cover_image_url（总表 vs 2026 表）
"""
import sqlite3
import os

db = r'G:\原创计划\music'
if os.path.isdir(db):
    db = os.path.join(db, 'music')

conn = sqlite3.connect(db)
c = conn.cursor()

lines = []

lines.append('=== albums 总表 - 张悬 cover_image_url ===')
c.execute("SELECT album_id, album_name, cover_image_url FROM albums WHERE artist LIKE '%张悬%' ORDER BY album_id")
rows = c.fetchall()
for r in rows:
    lines.append(f'  id={r[0]} | {r[1]} | cover={r[2]}')
lines.append('')

lines.append('=== albums_2026 表 - 张悬 cover_image_url ===')
try:
    c.execute("SELECT album_id, album_name, artist, cover_image_url FROM albums_2026 WHERE album_name LIKE '%城市%' OR album_name LIKE '%神的游戏%' ORDER BY album_id")
    rows2 = c.fetchall()
    for r in rows2:
        lines.append(f'  id={r[0]} | {r[1]} | artist={r[2]} | cover={r[3]}')
except Exception as e:
    lines.append(f'Error: {e}')
lines.append('')

# 检查封面文件是否存在
covers_dir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\covers'
lines.append(f'=== 检查封面文件是否存在 (covers_dir={covers_dir}) ===')
if os.path.exists(covers_dir):
    files = os.listdir(covers_dir)
    # 检查总表的 cover
    for r in rows:
        cover = r[2]
        if cover:
            fname = cover.replace('covers/', '')
            exists = fname in files
            lines.append(f'  {fname} -> {"OK 存在" if exists else "NOT 不存在"}')
    # 检查 2026 表的 cover
    for r in rows2:
        cover = r[3]
        if cover:
            fname = cover.replace('covers/', '')
            exists = fname in files
            lines.append(f'  {fname} -> {"OK 存在" if exists else "NOT 不存在"}')
else:
    lines.append(f'封面目录不存在: {covers_dir}')

conn.close()

output = '\n'.join(lines)

with open(r'C:\Users\qujt\.qclaw\workspace\zx_cover_check.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print('Done, saved to zx_cover_check.txt')
