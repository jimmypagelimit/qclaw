import sqlite3, json

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()

result = {}

# Missing count
c.execute("SELECT COUNT(*) FROM tracks")
result['total_tracks'] = c.fetchone()[0]
c.execute("""SELECT COUNT(*) FROM tracks WHERE (lyrics_text_path IS NOT NULL AND lyrics_text_path != '') OR (lyrics_lrc_path IS NOT NULL AND lyrics_lrc_path != '')""")
result['has_lyrics'] = c.fetchone()[0]
result['coverage_pct'] = round(result['has_lyrics'] / result['total_tracks'] * 100, 1)
result['missing'] = result['total_tracks'] - result['has_lyrics']

# Top artists with missing lyrics
c.execute("""SELECT a.artist, COUNT(*) as cnt FROM tracks t JOIN albums a ON t.album_id = a.album_id 
    WHERE (t.lyrics_text_path IS NULL OR t.lyrics_text_path = '') AND (t.lyrics_lrc_path IS NULL OR t.lyrics_lrc_path = '') 
    GROUP BY a.artist ORDER BY cnt DESC LIMIT 20""")
result['top_missing_artists'] = [[r[0], r[1]] for r in c.fetchall()]

# Check if _lyrics_batch.py exists
import os
batch_script = r'C:\Users\qujt\.qclaw\workspace\_lyrics_batch.py'
result['batch_script_exists'] = os.path.exists(batch_script)

# Check existing lyrics dir structure
lyrics_dir = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics'
if os.path.exists(lyrics_dir):
    artists = os.listdir(lyrics_dir)
    result['lyrics_dir_artists'] = len(artists)
else:
    result['lyrics_dir_artists'] = 0

with open(r'C:\Users\qujt\.qclaw\workspace\_lyrics_status.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

conn.close()
print('Status written to _lyrics_status.json')
