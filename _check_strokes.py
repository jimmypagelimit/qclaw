import sqlite3
db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute("SELECT album_id, album_name, release_year, total_listen_count FROM albums WHERE artist LIKE '%Strokes%'")
for r in c.fetchall():
    print(r)
conn.close()
