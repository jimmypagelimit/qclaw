import sqlite3, json
db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute("SELECT album_id, album_name, artist, cover_image_url FROM albums WHERE album_id=428")
row = cur.fetchone()
if row:
    result = {'id': row[0], 'name': row[1], 'artist': row[2], 'cover': row[3]}
    with open(r'C:\Users\qujt\.qclaw\workspace\_temp_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False)
conn.close()
