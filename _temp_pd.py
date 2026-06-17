import sqlite3
conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()
cur.execute("SELECT album_id, album_name, artist, cover_image_url FROM albums WHERE album_name LIKE '%Picture Day%'")
for r in cur.fetchall():
    print(r)
conn.close()
