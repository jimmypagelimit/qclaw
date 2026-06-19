"""LRCLIB 命中率抽样检查"""
import json, urllib.request, urllib.parse, sqlite3, time, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
LRCLIB = "https://lrclib.net/api/search?q="
UA = "AlbumTracker/1.0 (jim@163.com)"

conn = sqlite3.connect(DB)
cur = conn.cursor()

# 选10张英文专辑检查
test_ids = [461, 263, 506, 31, 233]  # Daydream Nation, Illmatic, Twilight Sad(It's the Long Goodbye), Disintegration, In Utero

for aid in test_ids:
    cur.execute("SELECT artist, album_name FROM albums WHERE album_id = ?", (aid,))
    artist, album = cur.fetchone()
    
    cur.execute("SELECT track_name FROM tracks WHERE album_id = ? ORDER BY disc_number, track_number LIMIT 5", (aid,))
    tracks = [r[0] for r in cur.fetchall()]
    
    print(f"\n=== {artist} - {album} ===")
    hits = 0
    for tname in tracks:
        q = f'{artist} {tname}'
        url = f'{LRCLIB}/{urllib.parse.quote(q)}'
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            r = json.loads(urllib.request.urlopen(req, timeout=8).read())
            if r and (r[0].get('syncedLyrics') or r[0].get('plainLyrics')):
                hits += 1
                print(f'  ✅ {tname[:40]}')
            else:
                print(f'  ❌ {tname[:40]} - no lyrics in result')
        except Exception as e:
            print(f'  ❌ {tname[:40]} - {type(e).__name__}')
        time.sleep(0.3)
    print(f'  => {hits}/{len(tracks)}')

conn.close()
