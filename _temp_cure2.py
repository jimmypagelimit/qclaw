import sqlite3, json
db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute("SELECT album_id, album_name, artist, cover_image_url FROM albums WHERE artist LIKE '%Cure%' OR album_name LIKE '%Cure%'")
rows = cur.fetchall()
result = []
for r in rows:
    result.append({'id': r[0], 'name': r[1], 'artist': r[2], 'cover': r[3]})
with open(r'C:\Users\qujt\.qclaw\workspace\_temp_cure.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False)
print(f'Found {len(result)} albums')
conn.close()
