import sqlite3

db = 'C:/Users/qujt/.qclaw/workspace/_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute("SELECT album_id, album_name, artist, cover_image_url FROM albums WHERE artist LIKE '%水木%' OR album_name LIKE '%青春正传%'")
rows = c.fetchall()
for r in rows:
    print(r)
conn.close()
