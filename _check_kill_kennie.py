import sqlite3, json

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT album_id, album_name, artist, cover_image_url FROM albums WHERE artist LIKE '%Kill%' OR artist LIKE '%Kennie%'")
rows = cur.fetchall()
for r in rows:
    print(json.dumps({'album_id': r[0], 'album_name': r[1], 'artist': r[2], 'cover_url': r[3]}, ensure_ascii=False))
conn.close()
