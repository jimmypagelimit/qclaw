import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
c = sqlite3.connect(db)
cur = c.cursor()
cur.execute('PRAGMA table_info(albums)')
for x in cur.fetchall():
    print(x)
