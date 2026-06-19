import sqlite3, os, json

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
lx = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics'

conn = sqlite3.connect(db, timeout=10)
c = conn.cursor()

# Albums with tracks
c.execute("""
SELECT a.album_id, a.album_name, a.artist, COUNT(t.id)
FROM albums a
JOIN tracks t ON a.album_id = t.album_id
GROUP BY a.album_id
ORDER BY a.album_id
""")
albums = c.fetchall()
print(f"DB albums with tracks: {len(albums)}")

# Albums already with lyrics
existing = set()
for artist_dir in os.listdir(lx):
    artist_path = os.path.join(lx, artist_dir)
    if os.path.isdir(artist_path):
        for album_dir in os.listdir(artist_path):
            existing.add((artist_dir, album_dir))
print(f"Lyrics folders: {len(existing)}")

# Match by name (approximate)
matched = 0
for aid, name, artist, tcount in albums:
    name_s = name.replace('/', '_').replace('\\', '_')
    for artist_dir, album_dir in existing:
        if artist_dir.lower() in artist.lower() or artist.lower() in artist_dir.lower():
            if album_dir.lower() in name_s.lower() or name_s.lower() in album_dir.lower():
                matched += 1
                break

print(f"Approximate matching albums with lyrics: {matched}")
print(f"Need lyrics: {len(albums) - matched}")

# Show top albums that need lyrics (first 10 without lyrics)
shown = 0
for aid, name, artist, tcount in albums:
    name_s = name.replace('/', '_').replace('\\', '_')
    found = False
    for artist_dir, album_dir in existing:
        if (artist_dir.lower() in artist.lower() or artist.lower() in artist_dir.lower()) and \
           (album_dir.lower() in name_s.lower() or name_s.lower() in album_dir.lower()):
            found = True
            break
    if not found and shown < 15:
        print(f"  NEED: ID {aid}: {artist} - {name} ({tcount} tracks)")
        shown += 1

conn.close()
