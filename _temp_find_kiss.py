import sqlite3

db = 'C:/Users/qujt/.qclaw/workspace/_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute("SELECT album_id, album_name, artist, cover_image_url FROM albums WHERE album_name LIKE '%Kiss%'")
rows = c.fetchall()
for r in rows:
    print(r)
conn.close()
