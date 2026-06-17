import sqlite3, json, urllib.request, urllib.parse, os, time

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
covers_dir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers'
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute('SELECT album_id, album_name, artist, cover_image_url FROM albums WHERE cover_image_url IS NULL OR cover_image_url = "" OR cover_image_url = "/covers/" ORDER BY album_id')
rows = cur.fetchall()
print(f'Total missing: {len(rows)}')
for r in rows:
    print(f"id={r[0]} name={r[1]} artist={r[2]}")
conn.close()
