#!/usr/bin/env python3
"""修复最后3个缺失字段"""
import sqlite3, os

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()

fixes = [
    (600, 'genre', '民谣'),
    (597, 'release_company', 'Century Media Records'),
    (593, 'release_company', '4AD'),
]

for aid, field, value in fixes:
    cur.execute(f'UPDATE albums SET {field}=? WHERE album_id=?', (value, aid))
    print(f'ID={aid}: set {field}="{value}"')

conn.commit()
conn.close()

# Export
conn = sqlite3.connect(DB)
with open(r'C:\Users\qujt\.qclaw\workspace\database.sql', 'w', encoding='utf-8') as f:
    for line in conn.iterdump():
        f.write(line + '\n')
conn.close()
print('SQL exported')
