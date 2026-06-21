# -*- coding: utf-8 -*-
"""
歌词批量补全 - 续跑版
从缺歌词的曲目中取下一批，用LRCLIB API补全
"""

import sqlite3
import urllib.request
import urllib.parse
import json
import time
import os
import sys

DB_PATH = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
LYRICS_DIR = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics'
LOG_FILE = r'C:\Users\qujt\.qclaw\workspace\_lyrics_fill_log.txt'
BATCH_SIZE = 50

def log(msg):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')
    print(msg)

def search_lrclib(artist, track_name):
    query = f"{artist} {track_name}"
    query_encoded = urllib.parse.quote(query)
    url = f"https://lrclib.net/api/search?q={query_encoded}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read().decode())
        if data and len(data) > 0:
            for item in data:
                if item.get('syncedLyrics'):
                    return item['syncedLyrics'], item.get('plainLyrics', '')
            if data[0].get('plainLyrics'):
                return None, data[0]['plainLyrics']
    except Exception as e:
        log(f"  ERROR lrclib: {e}")
    return None, None

def save_lyrics(artist, album_name, track_name, lrc_content, txt_content):
    artist_dir = os.path.join(LYRICS_DIR, artist)
    album_dir = os.path.join(artist_dir, album_name)
    os.makedirs(album_dir, exist_ok=True)
    
    # Sanitize filename
    safe_name = track_name.replace('/', '-').replace('\\', '-').replace(':', '-')
    
    paths = {}
    if lrc_content:
        p = os.path.join(album_dir, f"{safe_name}.lrc")
        with open(p, 'w', encoding='utf-8') as f:
            f.write(lrc_content)
        paths['lrc'] = p
    if txt_content:
        p = os.path.join(album_dir, f"{safe_name}.txt")
        with open(p, 'w', encoding='utf-8') as f:
            f.write(txt_content)
        paths['txt'] = p
    return paths

def main():
    batch_num = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Get missing lyrics tracks, skip already processed
    c.execute("""
        SELECT t.id, t.album_id, t.track_name, a.artist, a.album_name
        FROM tracks t JOIN albums a ON t.album_id = a.album_id
        WHERE (t.lyrics_text_path IS NULL OR t.lyrics_text_path = '')
          AND (t.lyrics_lrc_path IS NULL OR t.lyrics_lrc_path = '')
        ORDER BY t.id
        LIMIT ? OFFSET ?
    """, (BATCH_SIZE, (batch_num - 1) * BATCH_SIZE))
    
    tracks = c.fetchall()
    if not tracks:
        log(f"Batch {batch_num}: No missing tracks found!")
        conn.close()
        return
    
    log(f"\n=== Batch {batch_num}: Processing {len(tracks)} tracks ===")
    
    stats = {'lrc': 0, 'txt': 0, 'miss': 0, 'error': 0}
    
    for track_id, album_id, track_name, artist, album_name in tracks:
        log(f"  [{track_id}] {artist} - {album_name} - {track_name}")
        
        lrc, txt = search_lrclib(artist, track_name)
        
        if lrc or txt:
            paths = save_lyrics(artist, album_name, track_name, lrc, txt)
            # Update DB
            updates = []
            if 'lrc' in paths:
                updates.append(f"lyrics_lrc_path = '{paths['lrc'].replace(chr(39), chr(39)+chr(39))}'")
                stats['lrc'] += 1
            if 'txt' in paths:
                updates.append(f"lyrics_text_path = '{paths['txt'].replace(chr(39), chr(39)+chr(39))}'")
                stats['txt'] += 1
            if updates:
                c.execute(f"UPDATE tracks SET {', '.join(updates)} WHERE id = {track_id}")
                conn.commit()
            log(f"    -> OK (lrc={bool(lrc)}, txt={bool(txt)})")
        else:
            stats['miss'] += 1
            log(f"    -> MISS")
        
        time.sleep(0.3)  # Rate limit
    
    conn.close()
    log(f"Batch {batch_num} done: LRC={stats['lrc']}, TXT={stats['txt']}, Miss={stats['miss']}, Error={stats['error']}")

if __name__ == '__main__':
    main()
