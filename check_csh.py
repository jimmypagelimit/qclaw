#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3, os

db = r'G:\原创计划\music'
if os.path.isdir(db):
    db = os.path.join(db, 'music')

conn = sqlite3.connect(db)
c = conn.cursor()

print('=== 查找 Car Seat Headrest - Twin Fantasy ===')
tables = ['albums', 'albums_2024', 'albums_2025', 'albums_2026']

for tbl in tables:
    try:
        c.execute(f"SELECT album_id, album_name, artist, total_listen_count, overall_score, cover_image_url FROM {tbl} WHERE artist LIKE '%Car Seat%' OR album_name LIKE '%Twin Fantasy%'")
        rows = c.fetchall()
        if rows:
            print(f'\n表: {tbl}')
            for r in rows:
                print(f'  id={r[0]} album={r[1]} artist={r[2]} tc={r[3]} score={r[4]}')
                print(f'  cover_url={r[5]}')
    except Exception as e:
        pass

conn.close()
print('\nDone')
