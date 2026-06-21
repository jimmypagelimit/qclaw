import sqlite3
db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
conn.text_factory = str
c = conn.cursor()
c.execute('PRAGMA table_info(listen_history)')
for r in c.fetchall():
    print(r)
conn.close()
