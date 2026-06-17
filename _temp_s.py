import sqlite3
db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
cur = conn.cursor()
# Get all info about album 428
cur.execute("SELECT * FROM albums WHERE album_id=428")
row = cur.fetchone()
if row:
    print("album_id:", row[0])
    print("album_name:", row[1])
    print("artist:", row[2])
    print("cover:", row[11])
    print("release_year:", row[24])
conn.close()
