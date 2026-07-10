import sqlite3, os, json

db = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
c = db.cursor()

# Get 10 broken paths with full context
c.execute("""
    SELECT t.id, t.lyrics_text_path, t.track_name, a.artist, a.album_name
    FROM tracks t
    JOIN albums a ON t.album_id = a.album_id
    WHERE t.lyrics_text_path IS NOT NULL AND t.lyrics_text_path != ''
""")
all_with_path = []
broken = []
for row in c.fetchall():
    tid, path, tname, artist, album = row
    all_with_path.append((tid, path, tname, artist, album))
    if not os.path.exists(path):
        broken.append((tid, path, tname, artist, album))

print(f'Total with path: {len(all_with_path)}')
print(f'Broken (file not found): {len(broken)}')
print()

# Check lyrics base dir
base_dir = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics'
print(f'Base dir exists: {os.path.exists(base_dir)}')

# See what the root of the broken paths looks like - are they relative paths?
# Check if paths with the base_dir prepended exist
fixed = 0
still_broken = 0
for tid, path, tname, artist, album in broken:
    # Try prepending base dir
    full_path = os.path.join(base_dir, path)
    if os.path.exists(full_path):
        fixed += 1
    else:
        # Try looking at different dir levels
        # Some paths might have a prefix like 'lyrics/'
        if path.startswith('lyrics\\') or path.startswith('lyrics/'):
            alt_full = os.path.join(r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert', path)
            if os.path.exists(alt_full):
                fixed += 1
        else:
            still_broken += 1

print(f'Can fix by prepending base_dir: {fixed}')
print(f'Truly broken: {still_broken}')

# Check some original paths
print('\nOriginal path samples:')
for tid, path, tname, artist, album in broken[:5]:
    full = os.path.join(base_dir, path)
    print(f'  DB: {repr(path)}')
    print(f'  +base: {repr(full)} exists={os.path.exists(full)}')

# Good paths - how are they stored?
c.execute("""
    SELECT t.lyrics_text_path 
    FROM tracks t 
    WHERE t.lyrics_text_path IS NOT NULL AND t.lyrics_text_path != ''
    LIMIT 5
""")
print('\nGood path samples:')
for row in c.fetchall():
    p = row[0]
    print(f'  {repr(p)} exists={os.path.exists(p)}')

db.close()
