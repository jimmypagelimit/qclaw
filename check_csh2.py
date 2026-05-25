#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3, os

db = r'G:\原创计划\music'
if os.path.isdir(db):
    db = os.path.join(db, 'music')

conn = sqlite3.connect(db)
c = conn.cursor()

lines = []
lines.append('=== 查找 Car Seat Headrest - Twin Fantasy ===')
lines.append('')

tables = ['albums', 'albums_2024', 'albums_2025', 'albums_2026']

for tbl in tables:
    try:
        c.execute(f"SELECT album_id, album_name, artist, total_listen_count, overall_score, cover_image_url FROM {tbl} WHERE artist LIKE '%Car Seat%' OR album_name LIKE '%Twin Fantasy%'")
        rows = c.fetchall()
        if rows:
            lines.append(f'表: {tbl}')
            for r in rows:
                lines.append(f'  id={r[0]} album={r[1]} artist={r[2]} tc={r[3]} score={r[4]}')
                lines.append(f'  cover_url={r[5]}')
                lines.append('')
    except Exception as e:
        lines.append(f'Error {tbl}: {e}')

conn.close()

output = '\n'.join(lines)
print(output)

with open(r'C:\Users\qujt\.qclaw\workspace\csh_result.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print('\nDone, saved to csh_result.txt')
