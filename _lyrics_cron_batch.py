"""
LRCLIB batch fetch for well-known indie artists.
Target: Car Seat Headrest, Big Thief, Sufjan Stevens, etc.
Keep runtime < 80s to avoid QEMU SIGKILL.
"""
import sqlite3, urllib.request, json, time, os, re

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
LYRICS_DIR = r'C:\Users\qujt\.qclaw\workspace\lyrics'

target_artists = [
    'Car Seat Headrest', 'Big Thief', 'Sufjan Stevens', 'The National',
    'Phoebe Bridgers', 'Mitski', 'Bon Iver', 'Arcade Fire',
    'Radiohead', 'LCD Soundsystem', 'Death Cab for Cutie',
    'Modest Mouse', 'Vampire Weekend', 'Grizzly Bear', 'Animal Collective'
]

conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute('''
SELECT t.track_name, al.artist, al.album_name, t.track_number, t.id
FROM tracks t
JOIN albums al ON t.album_id = al.album_id
WHERE t.lyrics_lrc_path IS NULL
AND al.artist IN (%s)
ORDER BY RANDOM()
LIMIT 40
''' % ','.join('?' * len(target_artists)), target_artists)

tracks = cur.fetchall()
conn.close()

print(f'Processing {len(tracks)} tracks...')
start = time.time()

found = 0
not_found = 0
errors = 0

for i, (track_name, artist, album_name, track_num, track_id) in enumerate(tracks):
    elapsed = time.time() - start
    if elapsed > 70:
        print(f'Time limit approaching ({elapsed:.0f}s), stopping at {i}')
        break
    
    try:
        # Search LRCLIB
        query = f'{artist} {track_name}'.replace(' ', '+')
        url = f'https://lrclib.net/api/search?q={query}'
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=8)
        results = json.loads(resp.read())
        
        if not results:
            not_found += 1
            print(f'  [{i+1}] NOT FOUND: {artist} - {track_name}')
            continue
        
        # Find best match
        best = None
        for r in results:
            r_artist = r.get('artistName', '').lower()
            r_name = r.get('trackName', '').lower()
            t_name = track_name.lower()
            
            # Check similarity
            if (artist.lower() in r_artist or r_artist in artist.lower()) and \
               (t_name in r_name or r_name in t_name or 
                abs(len(t_name) - len(r_name)) < 5):
                if best is None or r.get('instrumental') == False:
                    best = r
        
        if best is None:
            best = results[0]  # fallback to first
        
        if best.get('instrumental'):
            not_found += 1
            print(f'  [{i+1}] INSTRUMENTAL: {artist} - {track_name}')
            continue
        
        lrc = best.get('syncedLyrics', '')
        if not lrc:
            not_found += 1
            print(f'  [{i+1}] NO SYNCED LRC: {artist} - {track_name}')
            continue
        
        # Save LRC file
        safe_artist = re.sub(r'[<>:"/\\|?*]', '_', artist)
        safe_album = re.sub(r'[<>:"/\\|?*]', '_', album_name)
        lrc_dir = os.path.join(LYRICS_DIR, safe_artist, safe_album)
        os.makedirs(lrc_dir, exist_ok=True)
        
        lrc_filename = f'{track_num:02d}.lrc'
        lrc_path = os.path.join(lrc_dir, lrc_filename)
        
        with open(lrc_path, 'w', encoding='utf-8') as f:
            f.write(lrc)
        
        # Update DB
        rel_path = f'{safe_artist}/{safe_album}/{lrc_filename}'
        conn2 = sqlite3.connect(DB)
        cur2 = conn2.cursor()
        cur2.execute(
            'UPDATE tracks SET lyrics_lrc_path = ? WHERE id = ?',
            (rel_path, track_id)
        )
        conn2.commit()
        conn2.close()
        
        found += 1
        print(f'  [{i+1}] FOUND: {artist} - {track_name} -> {rel_path}')
        
    except Exception as e:
        errors += 1
        print(f'  [{i+1}] ERROR: {artist} - {track_name}: {e}')

total_time = time.time() - start
print(f'\n=== DONE ({total_time:.1f}s) ===')
print(f'Found: {found}, Not found: {not_found}, Errors: {errors}')
