import sqlite3

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute("SELECT album_id, album_name, artist FROM albums WHERE artist LIKE '%苏醒%'")
for row in cur.fetchall():
    print(f'[{row[0]}] {row[2]} - {row[1]}')
conn.close()
