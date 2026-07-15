import sqlite3, os, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
LYRICS_DIR = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics'

conn = sqlite3.connect(DB)
cur = conn.cursor()

# Get all missing tracks with artist/album/track info
cur.execute('''
    SELECT a.artist, a.album_name, t.track_name, t.id
    FROM tracks t
    JOIN albums a ON t.album_id = a.album_id
    WHERE (t.lyrics_lrc_path IS NULL OR t.lyrics_lrc_path = "")
      AND (t.lyrics_text_path IS NULL OR t.lyrics_text_path = "")
''')
missing = cur.fetchall()
conn.close()

print(f'Missing tracks: {len(missing)}')

# Check which of these have lyrics files on disk
found_on_disk = 0
not_on_disk = []

# Build a quick lookup of lyrics files
lyrics_files = {}
for dirpath, dirs, files in os.walk(LYRICS_DIR):
    for f in files:
        if f.endswith(('.txt', '.lrc')):
            key = f.rsplit('.', 1)[0]  # filename without extension
            lyrics_files[key] = os.path.join(dirpath, f)

print(f'Lyrics files on disk: {len(lyrics_files)}')

# Try to match
for artist, album, track, track_id in missing:
    # Try various filename patterns
    candidates = [
        track,  # exact track name
        track.replace(' ', '_'),
        track.replace(' ', '-'),
    ]
    matched = False
    for c in candidates:
        if c in lyrics_files:
            found_on_disk += 1
            matched = True
            break
    if not matched:
        not_on_disk.append((artist, album, track))

print(f'Can be matched from disk: {found_on_disk}')
print(f'Still truly missing: {len(not_on_disk)}')

# Show some not-on-disk
print('\nSample not-on-disk (first 15):')
for artist, album, track in not_on_disk[:15]:
    print(f'  {artist} | {album} | {track}')

# Check what artists are in the not-on-disk list
from collections import Counter
artists = Counter([a for a, _, _ in not_on_disk])
print(f'\nTop missing artists (not on disk):')
for artist, cnt in artists.most_common(10):
    print(f'  {artist}: {cnt}')
