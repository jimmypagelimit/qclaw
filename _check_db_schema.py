import sqlite3
db = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\_music_latest.db'
conn = sqlite3.connect(db)
cur = conn.cursor()
# Get max album_id
cur.execute("SELECT MAX(album_id) FROM albums")
print(f"Max album_id: {cur.fetchone()[0]}")
# Get max listen_history id
cur.execute("SELECT MAX(id) FROM listen_history")
print(f"Max listen_history.id: {cur.fetchone()[0]}")
# Get column info for albums
cur.execute("PRAGMA table_info(albums)")
cols = cur.fetchall()
for c in cols:
    print(f"  {c}")
conn.close()
