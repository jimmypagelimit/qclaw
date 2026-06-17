import sqlite3
conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()
cur.execute("SELECT album_id, album_name, artist, cover_image_url FROM albums WHERE album_name LIKE \"%Nothing%About%Happen%\" OR album_name LIKE \"%Mitski%\"")
for r in cur.fetchall():
    print(r[0], '|', r[1], '|', r[2], '|', r[3])
conn.close()
