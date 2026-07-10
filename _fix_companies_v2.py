#!/usr/bin/env python3
"""修正发行公司"""
import sqlite3, os

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'

# 正确的发行公司
company_fixes = [
    (602, 'Pancamama'),       # The Microphones - The Glow, Pt. 2
    (601, 'Fiction Records'),  # The Cure - Songs of a Lost World
    (599, '独立发行'),         # 碎梦飞跃 - 外面是夏天
    (596, '索雅音乐'),         # 郑源 - 擦肩而过
]

conn = sqlite3.connect(DB)
cur = conn.cursor()

print('=== Fix release companies ===\n')

for album_id, company in company_fixes:
    cur.execute('SELECT album_name, artist FROM albums WHERE album_id=?', (album_id,))
    row = cur.fetchone()
    if row:
        album_name, artist = row
        cur.execute('UPDATE albums SET release_company=? WHERE album_id=?', (company, album_id))
        print(f'ID={album_id}: {artist} - {album_name} -> {company}')
    else:
        print(f'ID={album_id}: not found')

conn.commit()
conn.close()

print('\n=== Export ===')
conn = sqlite3.connect(DB)
with open(r'C:\Users\qujt\.qclaw\workspace\database.sql', 'w', encoding='utf-8') as f:
    for line in conn.iterdump():
        f.write(line + '\n')
conn.close()
print('Done')
