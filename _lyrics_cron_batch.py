"""
歌词计划 Cron 批次 - 2026-07-16
目标：处理 top missing artists (confirmed LRCLIB coverage)
"""
import sqlite3, urllib.request, urllib.parse, json, os, time

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
LYRICS_DIR = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics'
UA = "AlbumTracker/1.0 (jim@example.com)"
LRCLIB_BASE = "https://lrclib.net/api"

def lrclib_search(artist, track, timeout=15):
    params = urllib.parse.urlencode({'q': f'{artist} {track}'})
    url = f"{LRCLIB_BASE}/search?{params}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception:
        return []

def lrclib_get(lrc_id, timeout=15):
    url = f"{LRCLIB_BASE}/get/{lrc_id}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception:
        return None

def save_lyrics(artist, album, track_name, lrc_text, plain_text):
    safe = lambda s: "".join(c for c in str(s) if c not in r'\/:*?"<>|').strip()
    base = os.path.join(LYRICS_DIR, safe(artist), safe(album))
    os.makedirs(base, exist_ok=True)
    lrc_path = txt_path = None
    if lrc_text:
        lrc_path = os.path.join(base, f"{safe(track_name)}.lrc")
        with open(lrc_path, 'w', encoding='utf-8') as f:
            f.write(lrc_text)
    if plain_text:
        txt_path = os.path.join(base, f"{safe(track_name)}.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(plain_text)
    return lrc_path, txt_path

def process_batch(conn, artist, album, batch_tracks):
    """批量处理一组曲目"""
    found = 0
    for track_id, track_name in batch_tracks:
        results = lrclib_search(artist, track_name)
        if not results:
            print(f"  [NONE] {track_name}")
            time.sleep(1)
            continue
        
        full = lrclib_get(results[0]['id'])
        if not full:
            print(f"  [ERR] {track_name}")
            time.sleep(1)
            continue
        
        lrc = full.get('syncedLyrics', '')
        plain = full.get('plainLyrics', '')
        
        if not lrc and not plain:
            print(f"  [EMPTY] {track_name}")
            time.sleep(1)
            continue
        
        lrc_path, txt_path = save_lyrics(artist, album, track_name, lrc, plain)
        cur = conn.cursor()
        cur.execute(
            "UPDATE tracks SET lyrics_lrc_path=?, lyrics_text_path=? WHERE id=?",
            (lrc_path, txt_path, track_id)
        )
        print(f"  [OK] {track_name}")
        found += 1
        time.sleep(1)
    
    conn.commit()
    return found

def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    
    # Priority artists (confirmed LRCLIB coverage + high missing count)
    # Skip Funeral Mist (black metal, no lyrics) and 赵季平 (film scores)
    priority_artists = [
        ("The Cure", 4),          # Classic rock - good LRCLIB coverage
        ("John Lennon", 3),        # Solo Beatles
        ("The Smiths", 2),         # Classic indie rock
        ("The Twilight Sad", 2),   # Scottish post-rock
    ]
    
    total_found = 0
    total_processed = 0
    
    for artist, max_albums in priority_artists:
        # Get albums by this artist missing lyrics
        cur.execute('''
            SELECT DISTINCT a.album_name, a.album_id
            FROM albums a
            JOIN tracks t ON t.album_id = a.album_id
            WHERE a.artist = ?
            AND (t.lyrics_lrc_path IS NULL OR t.lyrics_text_path IS NULL)
            LIMIT ?
        ''', (artist, max_albums))
        
        albums = cur.fetchall()
        if not albums:
            print(f"\n[SKIP] {artist} - no albums need lyrics")
            continue
        
        print(f"\n{'='*60}")
        print(f"Processing: {artist} ({len(albums)} albums)")
        print(f"{'='*60}")
        
        for album_name, album_id in albums:
            # Get tracks missing lyrics for this album
            cur.execute('''
                SELECT t.id, t.track_name
                FROM tracks t
                WHERE t.album_id = ?
                AND t.lyrics_lrc_path IS NULL AND t.lyrics_text_path IS NULL
                ORDER BY t.track_number
            ''', (album_id,))
            tracks = cur.fetchall()
            
            if not tracks:
                print(f"\n  [DONE] {album_name}")
                continue
            
            print(f"\n  Album: {album_name} ({len(tracks)} tracks)")
            
            # Take up to 10 tracks per album
            batch = tracks[:10]
            found = process_batch(conn, artist, album_name, batch)
            total_found += found
            total_processed += len(batch)
            
            if found > 0:
                print(f"  -> Found {found}/{len(batch)}")
            
            time.sleep(2)  # Gap between albums
    
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"Cron Run Complete")
    print(f"Processed: {total_processed} tracks")
    print(f"Found lyrics: {total_found}")
    print(f"{'='*60}")
    
    # Update status
    status = {
        "total_tracks": 5024,
        "has_lyrics": 4310 + total_found,
        "coverage_pct": round((4310 + total_found) / 5024 * 100, 1),
        "missing": 714 - total_found,
        "cron_run": "2026-07-16",
        "found_this_run": total_found,
        "processed_this_run": total_processed
    }
    with open(r'C:\Users\qujt\.qclaw\workspace\_lyrics_status.json', 'w', encoding='utf-8') as f:
        json.dump(status, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    main()
