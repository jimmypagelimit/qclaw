import sqlite3, json, urllib.request, urllib.parse, os, sys

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
covers_dir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers'
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute('SELECT album_id, album_name, artist, cover_image_url FROM albums WHERE cover_image_url IS NULL OR cover_image_url = "" OR cover_image_url = "/covers/" ORDER BY album_id')
rows = cur.fetchall()
result = []
for r in rows:
    result.append({'id': r[0], 'name': r[1], 'artist': r[2], 'cover': r[3]})
with open(r'C:\Users\qujt\.qclaw\workspace\_missing_covers.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False)
print(f'Total missing: {len(result)}')
conn.close()
