#!/usr/bin/env python3
"""补充发行公司（基于搜索结果）"""
import sqlite3, os

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'

# 补充发行公司（基于搜索结果和网络信息）
company_fixes = [
    (602, 'Pancamama'),         # The Microphones
    (601, 'Fiction Records'),    # The Cure
    (599, '独立发行'),           # 碎梦飞跃
    (598, 'RCA Records'),        # Ryan Beatty
    (596, '索雅音乐'),           # 郑源
    (595, 'MNRK Music Group'),   # Fires in the Distance
    (594, 'Svart Records'),      # Warning
]

conn = sqlite3.connect(DB)
cur = conn.cursor()

print('=== Update release companies ===\n')

for album_id, company in company_fixes:
    cur.execute('SELECT album_name, artist, release_company FROM albums WHERE album_id=?', (album_id,))
    row = cur.fetchone()
    if row:
        album_name, artist, current = row
        if not current or current in ['', '??']:
            cur.execute('UPDATE albums SET release_company=? WHERE album_id=?', (company, album_id))
            print(f'ID={album_id}: {artist} - {album_name} -> {company}')
        else:
            ascii_current = current.encode('ascii', 'ignore').decode('ascii')
            print(f'ID={album_id}: {artist} - {album_name}: already has "{ascii_current}"')
    else:
        print(f'ID={album_id}: not found in database')

conn.commit()
conn.close()

print('\n=== Export ===')
conn = sqlite3.connect(DB)
with open(r'C:\Users\qujt\.qclaw\workspace\database.sql', 'w', encoding='utf-8') as f:
    for line in conn.iterdump():
        f.write(line + '\n')
conn.close()
print('Done')
