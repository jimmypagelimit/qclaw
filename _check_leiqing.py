import sqlite3, json

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("SELECT album_id, album_name, artist FROM albums WHERE album_name LIKE '%春子%' AND artist LIKE '%雷擎%'")
rows = c.fetchall()
for r in rows:
    print(json.dumps({'album_id': r[0], 'album_name': r[1], 'artist': r[2]}, ensure_ascii=False))
conn.close()
