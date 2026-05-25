#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3, os

db = r'G:\原创计划\music'
if os.path.isdir(db):
    db = os.path.join(db, 'music')

conn = sqlite3.connect(db)
c = conn.cursor()

lines = []

c.execute("SELECT album_id, album_name, artist, total_listen_count, overall_score, first_listen_date, cover_image_url FROM albums WHERE album_name LIKE '%Twin Fantasy%'")
rows = c.fetchall()
lines.append('=== albums 总表 ===')
for r in rows:
    lines.append(f'id={r[0]}')
    lines.append(f'  album={r[1]}')
    lines.append(f'  artist={r[2]}')
    lines.append(f'  first_listen={r[5]}')
    lines.append(f'  cover={r[6]}')
    lines.append('')

for year in [2024, 2025, 2026]:
    tbl = f'albums_{year}'
    try:
        c.execute(f"SELECT album_id, album_name, artist, first_listen_date, cover_image_url FROM {tbl} WHERE album_name LIKE '%Twin Fantasy%'")
        rows2 = c.fetchall()
        if rows2:
            lines.append(f'=== {tbl} ===')
            for r in rows2:
                lines.append(f'  id={r[0]} album={r[1]} artist={r[2]} first_listen={r[3]} cover={r[4]}')
    except:
        pass

conn.close()

output = '\n'.join(lines)
print(output)

with open(r'C:\Users\qujt\.qclaw\workspace\twin_fantasy_detail.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print('\nDone, saved to twin_fantasy_detail.txt')
