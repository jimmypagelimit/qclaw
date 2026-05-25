#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3, os, json

db = r'G:\原创计划\music'
if os.path.isdir(db):
    db = os.path.join(db, 'music')

print('DB:', db, 'exists:', os.path.exists(db))
conn = sqlite3.connect(db)
c = conn.cursor()

# 查所有张悬相关（繁体+简体+英文名）
keywords = ['张悬', '張懸', 'Deserts', 'Deserts Chang']
all_rows = []

for kw in keywords:
    for tbl in ['albums', 'albums_2024', 'albums_2025', 'albums_2026']:
        try:
            c.execute(f"SELECT album_id, album_name, artist, total_listen_count, overall_score, first_listen_date FROM {tbl} WHERE artist LIKE '%{kw}%' OR album_name LIKE '%{kw}%'")
            for row in c.fetchall():
                all_rows.append((tbl,) + row)
        except:
            pass

print('\n=== 所有张悬相关专辑 ===')
for r in all_rows:
    print(r)

conn.close()
print('\nDone - total:', len(all_rows))
