#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3
import os

db = r'G:\原创计划\music'
if os.path.isdir(db):
    db = os.path.join(db, 'music')

print('DB:', db, 'exists:', os.path.exists(db))

conn = sqlite3.connect(db)
c = conn.cursor()

# 查所有含张悬/張懸的专辑（albums总表）
c.execute("SELECT album_id, album_name, artist, total_listen_count, overall_score FROM albums WHERE artist LIKE '%张悬%' OR artist LIKE '%張懸%' OR artist LIKE '%Deserts%'")
rows = c.fetchall()
print('\n=== albums 总表 ===')
for r in rows:
    print(r)

# 查各年份表
for year in [2024, 2025, 2026]:
    tbl = f'albums_{year}'
    try:
        c.execute(f"SELECT album_id, album_name, artist, total_listen_count, overall_score FROM {tbl} WHERE artist LIKE '%张悬%' OR artist LIKE '%張懸%' OR artist LIKE '%Deserts%'")
        rows2 = c.fetchall()
        if rows2:
            print(f'\n=== {tbl} ===')
            for r in rows2:
                print(r)
    except Exception as e:
        pass

conn.close()
print('\nDone')
