import sqlite3, datetime
db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute("SELECT album_id, album_name, artist FROM albums WHERE artist LIKE ? OR album_name LIKE ?", ('%陈楚生%', '%荒芜%'))
rows = cur.fetchall()
if not rows:
    print('NOT FOUND')
for r in rows:
    print(r)
conn.close()
