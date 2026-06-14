import sqlite3
DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:", [r[0] for r in cur.fetchall()])
cur.execute("PRAGMA table_info(artists)")
print("artists columns:", [(r[1], r[2]) for r in cur.fetchall()])
cur.execute("PRAGMA table_info(albums)")
print("albums columns:", [(r[1], r[2]) for r in cur.fetchall()])
conn.close()
