import sqlite3, os

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'

conn = sqlite3.connect(DB)
cur = conn.cursor()

total = cur.execute('SELECT COUNT(*) FROM tracks').fetchone()[0]
has_lrc = cur.execute('SELECT COUNT(*) FROM tracks WHERE lyrics_lrc_path IS NOT NULL AND lyrics_lrc_path != ""').fetchone()[0]
has_text = cur.execute('SELECT COUNT(*) FROM tracks WHERE lyrics_text_path IS NOT NULL AND lyrics_text_path != ""').fetchone()[0]
has_any = cur.execute('''
    SELECT COUNT(*) FROM tracks 
    WHERE (lyrics_lrc_path IS NOT NULL AND lyrics_lrc_path != "")
       OR (lyrics_text_path IS NOT NULL AND lyrics_text_path != "")
''').fetchone()[0]
missing = cur.execute('''
    SELECT COUNT(*) FROM tracks 
    WHERE (lyrics_lrc_path IS NULL OR lyrics_lrc_path = "")
      AND (lyrics_text_path IS NULL OR lyrics_text_path = "")
''').fetchone()[0]

print(f'Total tracks: {total}')
print(f'Has LRC path: {has_lrc} ({has_lrc*100/total:.1f}%)')
print(f'Has text path: {has_text} ({has_text*100/total:.1f}%)')
print(f'Has any lyrics: {has_any} ({has_any*100/total:.1f}%)')
print(f'Missing lyrics: {missing} ({missing*100/total:.1f}%)')

# Show top missing artists - join with albums to get artist name
cur.execute('''
    SELECT a.artist, COUNT(*) as cnt
    FROM tracks t
    JOIN albums a ON t.album_id = a.album_id
    WHERE (t.lyrics_lrc_path IS NULL OR t.lyrics_lrc_path = "")
      AND (t.lyrics_text_path IS NULL OR t.lyrics_text_path = "")
    GROUP BY a.artist
    ORDER BY cnt DESC
    LIMIT 10
''')
print('\nTop missing artists:')
for row in cur.fetchall():
    print(f'  {row[0]}: {row[1]}')

# Check which external lyrics directories are accessible
print('\n--- External lyrics check ---')
for base in [r'H:\私人\荒岛唱片', r'C:\荒岛唱片']:
    for sub in ['lyrics', 'lyrics_lrc']:
        p = os.path.join(base, sub)
        exists = os.path.exists(p)
        print(f'{p}: {exists}')

conn.close()
