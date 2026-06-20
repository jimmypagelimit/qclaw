import sqlite3, urllib.request, json
from datetime import date

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB)
c = conn.cursor()

album_id = 543

# Check schema
c.execute("PRAGMA table_info(listen_history)")
cols = c.fetchall()
for col in cols:
    print(col)

# Check existing data sample
c.execute("SELECT * FROM listen_history LIMIT 1")
row = c.fetchone()
if row:
    print(f"Sample: {row}")
else:
    print("No rows")

conn.close()
