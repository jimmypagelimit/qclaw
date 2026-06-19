import sqlite3, sys, urllib.request, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

cur.execute("SELECT album_id, artist, album_name, release_mbid FROM albums WHERE album_id = 424")
r = cur.fetchone()
print(f'ID={r[0]} {r[1]} - {r[2]} MBID={r[3]}')
print()

cur.execute("SELECT track_id, track_number, disc_number, track_name, duration FROM tracks WHERE album_id = 424 ORDER BY disc_number, track_number")
tracks = cur.fetchall()
print(f'Tracks: {len(tracks)}')
for t in tracks:
    track_id, tn, dn, name, dur = t
    print(f'  [{dn}:{tn}] {name} ({dur}s)')

conn.close()
