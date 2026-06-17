import sqlite3

db = 'C:/Users/qujt/.qclaw/workspace/_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute("PRAGMA table_info(albums)")
rows = c.fetchall()
for r in rows:
    print(r)
conn.close()
