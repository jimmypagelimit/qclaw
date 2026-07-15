import sqlite3, os

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()

# Check what paths are stored in the DB
cur.execute('''
    SELECT lyrics_lrc_path, COUNT(*) as cnt
    FROM tracks
    WHERE lyrics_lrc_path IS NOT NULL AND lyrics_lrc_path != ""
    GROUP BY 1
    ORDER BY cnt DESC
    LIMIT 20
''')
print('Sample LRC paths in DB:')
for row in cur.fetchall():
    print(f'  {row[0]}: {row[1]}')

# Check if any local lyrics exist
local_lyrics = r'C:\Users\qujt\.qclaw\workspace\lyrics'
if os.path.exists(local_lyrics):
    files = os.listdir(local_lyrics)
    print(f'\nLocal lyrics dir exists: {len(files)} files')
    if files:
        print('Sample:', files[:5])
else:
    print(f'\nLocal lyrics dir does not exist: {local_lyrics}')

# Check a specific missing track
cur.execute('''
    SELECT a.artist, a.album_name, t.track_name, t.lyrics_lrc_path, t.lyrics_text_path
    FROM tracks t
    JOIN albums a ON t.album_id = a.album_id
    WHERE (t.lyrics_lrc_path IS NULL OR t.lyrics_lrc_path = "")
      AND (t.lyrics_text_path IS NULL OR t.lyrics_text_path = "")
    LIMIT 5
''')
print('\nSample missing tracks:')
for row in cur.fetchall():
    print(f'  {row[0]} - {row[1]} - {row[2]}')
    print(f'    LRC: {row[3]}')
    print(f'    TXT: {row[4]}')

conn.close()
