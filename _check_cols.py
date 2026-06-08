import sqlite3
db_path = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute('PRAGMA table_info(albums)')
for row in cur.fetchall():
    print(row)
conn.close()