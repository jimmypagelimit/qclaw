import sqlite3, urllib.request, urllib.parse, json, os, sys

# Fix stdout encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'

conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute('''
    SELECT a.artist, a.album_name, t.track_name, t.id
    FROM tracks t
    JOIN albums a ON t.album_id = a.album_id
    WHERE (t.lyrics_lrc_path IS NULL OR t.lyrics_lrc_path = "")
      AND (t.lyrics_text_path IS NULL OR t.lyrics_text_path = "")
    ORDER BY RANDOM()
    LIMIT 20
''')
missing_tracks = cur.fetchall()
conn.close()

print(f'Found {len(missing_tracks)} missing tracks. Trying LRCLIB...\n')

found = 0
errors = 0

for artist, album, track, track_id in missing_tracks:
    q = f'{artist} {track}'
    encoded = urllib.parse.quote(q)
    url = f'https://lrclib.net/api/search?q={encoded}'
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        
        if data:
            best = data[0]
            lrc = best.get('plainLyrics') or best.get('syncedLyrics', '')
            if lrc:
                print(f'[FOUND] {artist} - {track}')
                print(f'        Album: {best.get("albumName", "?")} | Duration: {best.get("duration", "?")}s')
                found += 1
            else:
                print(f'[EMPTY] {artist} - {track}')
        else:
            print(f'[NONE]  {artist} - {track}')
    except Exception as e:
        print(f'[ERR]   {artist} - {track}: {e}')
        errors += 1
    
    import time
    time.sleep(0.3)

print(f'\nResult: {found} found, {errors} errors, {20-found-errors} not found')
