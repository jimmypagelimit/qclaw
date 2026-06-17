import sqlite3
db = sqlite3.connect(r"C:\Users\qujt\.qclaw\workspace\_music_latest.db")
total_albums = db.execute("SELECT COUNT(*) FROM albums").fetchone()[0]
with_tracks = db.execute("SELECT COUNT(DISTINCT album_id) FROM tracks").fetchone()[0]
total_tracks = db.execute("SELECT COUNT(*) FROM tracks").fetchone()[0]
print(f"albums: {total_albums}, with tracks: {with_tracks}, total tracks: {total_tracks}")
print()
srcs = db.execute("SELECT source, COUNT(*) FROM tracks GROUP BY source").fetchall()
for s, c in srcs:
    print(f"  source={s}: {c}")
print()
rows = db.execute("""
    SELECT a.album_id, a.album_name, a.artist, COUNT(t.id) as num
    FROM albums a
    JOIN tracks t ON a.album_id = t.album_id
    GROUP BY a.album_id
    ORDER BY a.album_id DESC
    LIMIT 10
""").fetchall()
for r in rows:
    print(f"  [{r[0]}] {repr(r[1])[:30]:<32} {repr(r[2])[:18]:<20} {r[3]} tracks")
db.close()
