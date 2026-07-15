import sqlite3, urllib.request, urllib.parse, json, sys, io, time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
OUT = r'C:\Users\qujt\.qclaw\workspace\_lyrics_quick_result.txt'

conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute('''
    SELECT a.artist, a.album_name, t.track_name, t.id
    FROM tracks t
    JOIN albums a ON t.album_id = a.album_id
    WHERE (t.lyrics_lrc_path IS NULL OR t.lyrics_lrc_path = "")
      AND (t.lyrics_text_path IS NULL OR t.lyrics_text_path = "")
    ORDER BY RANDOM()
    LIMIT 10
''')
missing = cur.fetchall()
conn.close()

results = []
found = 0

for artist, album, track, track_id in missing:
    q = f'{artist} {track}'
    url = f'https://lrclib.net/api/search?q={urllib.parse.quote(q)}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=8)
        data = json.loads(resp.read())
        if data:
            best = data[0]
            lrc = best.get('plainLyrics') or best.get('syncedLyrics', '')
            if lrc:
                results.append(f'[FOUND] {artist} | {album} | {track} | {best.get("albumName","?")} | {best.get("duration","?")}s')
                found += 1
            else:
                results.append(f'[EMPTY] {artist} | {album} | {track}')
        else:
            results.append(f'[NONE]  {artist} | {album} | {track}')
    except Exception as e:
        results.append(f'[ERR]   {artist} | {album} | {track} | {e}')
    time.sleep(0.3)

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(f'Found {found}/{len(missing)}:\n')
    for r in results:
        f.write(r + '\n')

print(f'Done: {found}/{len(missing)} found')
