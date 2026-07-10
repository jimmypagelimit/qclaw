import sqlite3
conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()
cur.execute("SELECT album_id, artist, album_name, release_year FROM albums WHERE artist LIKE '%Natalia%' OR album_name LIKE '%Hasta%'")
for r in cur.fetchall():
    print(r)
conn.close()
