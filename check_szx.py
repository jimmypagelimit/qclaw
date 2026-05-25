#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查苏紫旭专辑是否已在库中
"""
import sqlite3
import os

db = r'G:\原创计划\music'
if os.path.isdir(db):
    db = os.path.join(db, 'music')

conn = sqlite3.connect(db)
c = conn.cursor()

lines = []

lines.append('=== 检查 苏紫旭 & The Paramecia ===')

# 检查总表
c.execute("""SELECT album_id, album_name, artist, total_listen_count, overall_score 
             FROM albums 
             WHERE artist LIKE '%苏紫旭%' OR album_name LIKE '%悲歌欢唱%'
             ORDER BY album_id""")
rows = c.fetchall()

if rows:
    lines.append(f'总表找到 {len(rows)} 条记录:')
    for r in rows:
        lines.append(f'  id={r[0]} | {r[1]} | {r[2]} | tc={r[3]} | score={r[4]}')
else:
    lines.append('总表：未找到（需要新增）')

lines.append('')

# 检查 2026 表
try:
    c.execute("""SELECT album_id, album_name, artist, total_listen_count, overall_score 
                 FROM albums_2026 
                 WHERE artist LIKE '%苏紫旭%' OR album_name LIKE '%悲歌欢唱%'
                 ORDER BY album_id""")
    rows2 = c.fetchall()
    
    if rows2:
        lines.append(f'2026 表找到 {len(rows2)} 条记录:')
        for r in rows2:
            lines.append(f'  id={r[0]} | {r[1]} | {r[2]} | tc={r[3]} | score={r[4]}')
    else:
        lines.append('2026 表：未找到（需要新增）')
except Exception as e:
    lines.append(f'2026 表查询失败: {e}')

lines.append('')
lines.append('=== RYM 信息 ===')
lines.append('专辑: 悲歌欢唱 Lamenting in Delight')
lines.append('艺术家: 苏紫旭 & The Paramecia')
lines.append('发行: 2026-05-15')
lines.append('风格: Folk Rock, Progressive Rock, Indie Folk')
lines.append('RYM 评分: 3.50 / 5.0 (8 ratings)')
lines.append('收听次数: 4')

conn.close()

output = '\n'.join(lines)

with open(r'C:\Users\qujt\.qclaw\workspace\check_suzixu.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print('Done, saved to check_suzixu.txt')
