import sqlite3, os
conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
c = conn.cursor()

# Total tracks
c.execute("SELECT COUNT(*) FROM tracks")
total = c.fetchone()[0]

# Tracks with lyrics paths
c.execute("SELECT COUNT(*) FROM tracks WHERE lyrics_text_path IS NOT NULL AND lyrics_text_path != ''")
with_path = c.fetchone()[0]

c.execute("SELECT COUNT(*) FROM tracks WHERE lyrics_lrc_path IS NOT NULL AND lyrics_lrc_path != ''")
with_lrc = c.fetchone()[0]

# Tracks without any lyrics
c.execute("SELECT COUNT(*) FROM tracks WHERE (lyrics_text_path IS NULL OR lyrics_text_path = '') AND (lyrics_lrc_path IS NULL OR lyrics_lrc_path = '')")
no_lyrics = c.fetchone()[0]

print(f'Total tracks: {total}')
print(f'With text lyrics path: {with_path}')
print(f'With LRC lyrics path: {with_lrc}')
print(f'No lyrics at all: {no_lyrics}')
print(f'Coverage: {(total - no_lyrics) / total * 100:.1f}%')

# Check how many lyrics files actually exist
c.execute("SELECT lyrics_text_path FROM tracks WHERE lyrics_text_path IS NOT NULL AND lyrics_text_path != '' LIMIT 200")
paths = [r[0] for r in c.fetchall()]
exist_count = sum(1 for p in paths if os.path.exists(p))
print(f'\nSample check (first 200 text paths): {exist_count}/200 files exist')

# Albums with missing lyrics
c.execute("""
    SELECT a.artist, a.album_name, COUNT(*) as cnt 
    FROM albums a JOIN tracks t ON t.album_id = a.album_id 
    WHERE (t.lyrics_text_path IS NULL OR t.lyrics_text_path = '') 
       AND (t.lyrics_lrc_path IS NULL OR t.lyrics_lrc_path = '') 
    GROUP BY a.album_id 
    ORDER BY cnt DESC 
    LIMIT 20
""")
print('\nTop albums with missing lyrics:')
for row in c.fetchall():
    print(f'  {row[0]} - {row[1]}: {row[2]} tracks')

conn.close()
