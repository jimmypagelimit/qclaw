import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# search for 海鹏森
cur.execute("SELECT album_id, artist, album_name FROM albums WHERE artist LIKE '%海%' OR album_name LIKE '%成长小说%'")
rows = cur.fetchall()
for r in rows:
    print(f'ID={r[0]} {repr(r[1])} - {repr(r[2])}')

# also try fuzzy search
print()
cur.execute("SELECT album_id, artist, album_name FROM albums WHERE album_name LIKE '%成长%'")
rows = cur.fetchall()
for r in rows:
    print(f'ID={r[0]} {repr(r[1])} - {repr(r[2])}')

conn.close()
