#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细检查张悬在 albums_2026 表的状态
"""
import sqlite3
import os

db = r'G:\原创计划\music'
if os.path.isdir(db):
    db = os.path.join(db, 'music')

conn = sqlite3.connect(db)
c = conn.cursor()

lines = []

lines.append('=== albums_2026 表 - 张悬（完整信息）===')
try:
    c.execute("""SELECT album_id, album_name, artist, total_listen_count, overall_score, first_listen_date, cover_image_url 
                 FROM albums_2026 
                 WHERE artist LIKE '%张悬%' OR artist LIKE '%張懸%'
                 ORDER BY album_id""")
    rows = c.fetchall()
    lines.append(f'找到 {len(rows)} 条记录:')
    for r in rows:
        lines.append(f'  id={r[0]}')
        lines.append(f'    album={r[1]}')
        lines.append(f'    artist={r[2]}')
        lines.append(f'    tc={r[3]} | score={r[4]}')
        lines.append(f'    first_listen={r[5]}')
        lines.append(f'    cover={r[6]}')
        lines.append('')
except Exception as e:
    lines.append(f'Error: {e}')
    import traceback
    lines.append(traceback.format_exc())

lines.append('')
lines.append('=== 检查专辑名是否为繁体 ===')
try:
    c.execute("SELECT album_id, album_name, artist FROM albums_2026 WHERE album_name LIKE '%遊%' OR album_name LIKE '%戲%' OR album_name LIKE '%張%'")
    rows2 = c.fetchall()
    if rows2:
        lines.append(f'Warning: 有 {len(rows2)} 条记录含繁体字:')
        for r in rows2:
            lines.append(f'  id={r[0]} | {r[1]} | {r[2]}')
    else:
        lines.append('OK: 无繁体专辑名')
except Exception as e:
    lines.append(f'Error: {e}')

conn.close()

output = '\n'.join(lines)

with open(r'C:\Users\qujt\.qclaw\workspace\zx_2026_detail.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print('Done, saved to zx_2026_detail.txt')
