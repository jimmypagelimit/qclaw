import sqlite3
conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()
cur.execute('SELECT album_name, artist, rym_rating FROM albums WHERE album_name="Twin Fantasy"')
print(cur.fetchone())
cur.execute('SELECT album_name, artist, rym_rating FROM albums WHERE rym_rating IS NOT NULL LIMIT 3')
print(cur.fetchall())
conn.close()