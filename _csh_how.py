import sqlite3
db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute("SELECT album_id FROM albums WHERE artist LIKE '%Car Seat Headrest%' AND album_name LIKE '%How to Leave Town%'")
row = c.fetchone()
if row:
    aid = row[0]
    c.execute("INSERT INTO listen_history (album_id, listen_date, listen_year, notes) VALUES (?, '2026-07-13', 2026, 'A项目')", (aid,))
    conn.commit()
    c.execute("SELECT COUNT(*) FROM listen_history WHERE album_id = ?", (aid,))
    print(c.fetchone()[0])
else:
    print('not found')
conn.close()
