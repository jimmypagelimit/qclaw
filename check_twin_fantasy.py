#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3, os

db = r'G:\原创计划\music'
if os.path.isdir(db):
    db = os.path.join(db, 'music')

conn = sqlite3.connect(db)
c = conn.cursor()

# 查 Twin Fantasy 的详细信息
c.execute("SELECT album_id, album_name, artist, total_listen_count, overall_score, first_listen_date, cover_image_url FROM albums WHERE album_name LIKE '%Twin Fantasy%'")
rows = c.fetchall()
print('=== albums 总表 ===')
for r in rows:
    print(f'id={r[0]}')
    print(f'  album={r[1]}')
    print(f'  artist={r[2]}')
    print(f'  first_listen={r[5]}')
    print(f'  cover={r[6]}')
    print()

# 也查年份表
for year in [2024, 2025, 2026]:
    tbl = f'albums_{year}'
    try:
        c.execute(f"SELECT album_id, album_name, artist, first_listen_date, cover_image_url FROM {tbl} WHERE album_name LIKE '%Twin Fantasy%'")
        rows2 = c.fetchall()
        if rows2:
            print(f'=== {tbl} ===')
            for r in rows2:
                print(f'  id={r[0]} album={r[1]} artist={r[2]} first_listen={r[3]} cover={r[4]}')
    except:
        pass

conn.close()
print('\nDone')
