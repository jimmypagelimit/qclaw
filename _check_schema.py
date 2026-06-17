import sqlite3
db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute("PRAGMA table_info(albums)")
rows = c.fetchall()
for row in rows:
    print(row)
conn.close()
