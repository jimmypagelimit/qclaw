import sys, os
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1)  # line-buffered
sys.stderr = sys.stdout

print("Starting L batch...", flush=True)

import sqlite3, urllib.request, urllib.parse, json, time

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
LRCLIB_BASE = "https://lrclib.net/api"
UA = "AlbumTracker/1.0 (jim@example.com)"
LYRICS_DIR = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics'
os.makedirs(LYRICS_DIR, exist_ok=True)

def safe(n):
    return "".join(c for c in n if c not in r'\\/:*?"<>|').strip()

def is_cn(t):
    return any('\u4e00'<=c<='\u9fff' for c in t)

print("Connecting DB...", flush=True)
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("""
    SELECT t.album_id, a.artist, a.album_name, t.track_name, t.track_number
    FROM tracks t JOIN albums a ON t.album_id = a.album_id
    WHERE (t.lyrics_text_path IS NULL OR t.lyrics_text_path = '')
       OR (t.lyrics_lrc_path IS NULL OR t.lyrics_lrc_path = '')
    ORDER BY a.artist, t.track_number
""")
rows = cur.fetchall()
conn.close()
print(f"DB OK, {len(rows)} missing tracks", flush=True)

en = [r for r in rows if not is_cn(r[1])]
targets = en[:20]
print(f"English: {len(en)}, batch test: {len(targets)}", flush=True)

ok = fail = no_l = 0
for i, (aid, artist, album, track, tnum) in enumerate(targets, 1):
    print(f'  [{i}/{len(targets)}] {artist} - {album} / {track}', flush=True)
    q = urllib.parse.quote(f'{artist} {track}')
    try:
        resp = json.loads(urllib.request.urlopen(f'{LRCLIB_BASE}/search?q={q}', timeout=15).read())
        if not resp:
            no_l += 1; print('    -- no results', flush=True); continue
    except Exception as e:
        fail += 1; print(f'    -- ERR: {e}', flush=True); continue
    
    try:
        full = json.loads(urllib.request.urlopen(f'{LRCLIB_BASE}/get/{resp[0]["id"]}', timeout=15).read())
    except:
        fail += 1; print('    -- get fail', flush=True); continue
    
    lrc = full.get('syncedLyrics', '') or ''
    plain = full.get('plainLyrics', '') or ''
    if not lrc and not plain:
        no_l += 1; print('    -- no content', flush=True); continue
    
    base = os.path.join(LYRICS_DIR, safe(artist), safe(album))
    os.makedirs(base, exist_ok=True)
    
    saved = []
    if lrc:
        with open(os.path.join(base, f'{safe(track)}.lrc'), 'w', encoding='utf-8') as f:
            f.write(lrc)
        saved.append('lrc')
    if plain:
        with open(os.path.join(base, f'{safe(track)}.txt'), 'w', encoding='utf-8') as f:
            f.write(plain)
        saved.append('txt')
    
    # update DB
    conn2 = sqlite3.connect(DB)
    cur2 = conn2.cursor()
    if lrc:
        cur2.execute("UPDATE tracks SET lyrics_lrc_path=? WHERE album_id=? AND track_name=?",
                     (f'lyrics/{safe(artist)}/{safe(album)}/{safe(track)}.lrc', aid, track))
    if plain:
        cur2.execute("UPDATE tracks SET lyrics_text_path=? WHERE album_id=? AND track_name=?",
                     (f'lyrics/{safe(artist)}/{safe(album)}/{safe(track)}.txt', aid, track))
    conn2.commit()
    conn2.close()
    
    ok += 1
    print(f'    OK: {",".join(saved)}', flush=True)
    time.sleep(0.8)

print(f'\nDone: OK={ok} FAIL={fail} NONE={no_l}', flush=True)
