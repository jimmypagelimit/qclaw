#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查张悬专辑当前状态（合并后）
只写文件，不打印到控制台（避免编码错误）
"""
import sqlite3
import os

db = r'G:\原创计划\music'
if os.path.isdir(db):
    db = os.path.join(db, 'music')

conn = sqlite3.connect(db)
c = conn.cursor()

lines = []

lines.append('=== albums 总表 - 张悬 ===')
c.execute("SELECT album_id, album_name, artist, total_listen_count, overall_score, first_listen_date FROM albums WHERE artist LIKE '%张悬%' ORDER BY album_id")
rows = c.fetchall()
lines.append(f'找到 {len(rows)} 条记录:')
for r in rows:
    lines.append(f'  id={r[0]} | {r[1]} | artist={r[2]} | tc={r[3]} | score={r[4]} | first_listen={r[5]}')
lines.append('')

# 检查是否有繁体残留
lines.append('=== 检查繁体残留 ===')
c.execute("SELECT album_id, album_name, artist FROM albums WHERE artist LIKE '%張懸%'")
rows2 = c.fetchall()
if rows2:
    lines.append(f'Warning: 仍有 {len(rows2)} 条繁体记录:')
    for r in rows2:
        lines.append(f'  id={r[0]} | {r[1]} | {r[2]}')
else:
    lines.append('OK: 无繁体残留')
lines.append('')

# 检查重复专辑名
lines.append('=== 检查重复专辑名 ===')
c.execute("SELECT album_name, COUNT(*) as cnt, GROUP_CONCAT(album_id) as ids FROM albums WHERE artist LIKE '%张悬%' GROUP BY album_name HAVING cnt > 1")
dups = c.fetchall()
if dups:
    lines.append(f'Warning: 有 {len(dups)} 个重复专辑名:')
    for d in dups:
        lines.append(f'  {d[0]} (id={d[2]}, 共{d[1]}条)')
else:
    lines.append('OK: 无重复专辑名')
lines.append('')

# 检查 albums_2026 表
lines.append('=== albums_2026 表 - 张悬 ===')
try:
    c.execute("SELECT album_id, album_name, artist, total_listen_count, overall_score FROM albums_2026 WHERE artist LIKE '%张悬%' ORDER BY album_id")
    rows3 = c.fetchall()
    lines.append(f'找到 {len(rows3)} 条记录:')
    for r in rows3:
        lines.append(f'  id={r[0]} | {r[1]} | tc={r[3]} | score={r[4]}')
except Exception as e:
    lines.append(f'Error: {e}')
lines.append('')

conn.close()

output = '\n'.join(lines)

# 只写文件，不打印到控制台
with open(r'C:\Users\qujt\.qclaw\workspace\zhangxuan_status.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print('Done, saved to zhangxuan_status.txt')
