import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# schema
cur.execute("PRAGMA table_info(tracks)")
cols = cur.fetchall()
for c in cols:
    print(c)

print()
cur.execute("SELECT * FROM tracks WHERE album_id = 424 ORDER BY disc_number, track_number")
tracks = cur.fetchall()
print(f'Tracks: {len(tracks)}')
for t in tracks[:15]:
    print(t)

conn.close()
