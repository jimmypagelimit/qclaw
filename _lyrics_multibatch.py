# -*- coding: utf-8 -*-
"""
歌词批量补全 - 多批次连续执行
运行5批LRCLIB查询，每批50首
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
NUM_BATCHES = 5

def log(msg):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

def search_lrclib(artist, track_name):
    query = f"{artist} {track_name}"
    url = f"https://lrclib.net/api/search?q={urllib.parse.quote(query)}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read().decode())
        if data:
            for item in data:
                if item.get('syncedLyrics'):
                    return item['syncedLyrics'], item.get('plainLyrics', '')
            if data[0].get('plainLyrics'):
                return None, data[0]['plainLyrics']
    except Exception as e:
        log(f"  ERROR: {e}")
    return None, None

def sanitize(name):
    return name.replace('/', '-').replace('\\', '-').replace(':', '-').replace('?', '').replace('*', '').replace('"', '').replace('<', '').replace('>', '').replace('|', '').strip()

def save_lyrics(artist, album_name, track_name, lrc_content, txt_content):
    safe_artist = sanitize(artist)
    safe_album = sanitize(album_name)
    safe_name = sanitize(track_name)
    album_dir = os.path.join(LYRICS_DIR, safe_artist, safe_album)
    os.makedirs(album_dir, exist_ok=True)
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
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    total_lrc = total_txt = total_miss = 0
    
    for batch in range(NUM_BATCHES):
        # Get missing tracks (random, skip instrumentals/demos/takes)
        c.execute("""
            SELECT t.id, t.album_id, t.track_name, a.artist, a.album_name
            FROM tracks t JOIN albums a ON t.album_id = a.album_id
            WHERE (t.lyrics_text_path IS NULL OR t.lyrics_text_path = '')
              AND (t.lyrics_lrc_path IS NULL OR t.lyrics_lrc_path = '')
              AND t.track_name NOT LIKE '%instrumental%'
              AND t.track_name NOT LIKE '%demo%'
              AND t.track_name NOT LIKE '%Take %'
              AND t.track_name NOT LIKE '%rehearsal%'
              AND t.track_name NOT LIKE '%rough%'
              AND t.track_name NOT LIKE '%Jam%'
            ORDER BY RANDOM()
            LIMIT ?
        """, (BATCH_SIZE,))
        tracks = c.fetchall()
        
        if not tracks:
            log(f"Batch {batch+1}: No more missing tracks!")
            break
        
        log(f"\n=== Batch {batch+1}/{NUM_BATCHES}: {len(tracks)} tracks ===")
        batch_lrc = batch_txt = batch_miss = 0
        
        for track_id, album_id, track_name, artist, album_name in tracks:
            lrc, txt = search_lrclib(artist, track_name)
            
            if lrc or txt:
                paths = save_lyrics(artist, album_name, track_name, lrc, txt)
                updates = []
                if 'lrc' in paths:
                    updates.append(f"lyrics_lrc_path = '{paths['lrc'].replace(chr(39), chr(39)+chr(39))}'")
                    batch_lrc += 1
                if 'txt' in paths:
                    updates.append(f"lyrics_text_path = '{paths['txt'].replace(chr(39), chr(39)+chr(39))}'")
                    batch_txt += 1
                if updates:
                    c.execute(f"UPDATE tracks SET {', '.join(updates)} WHERE id = {track_id}")
                    conn.commit()
                log(f"  [{track_id}] OK: {artist} - {track_name} (lrc={bool(lrc)})")
            else:
                batch_miss += 1
            
            time.sleep(0.3)
        
        total_lrc += batch_lrc
        total_txt += batch_txt
        total_miss += batch_miss
        log(f"Batch {batch+1} done: +{batch_lrc}LRC +{batch_txt}TXT, {batch_miss}miss")
    
    conn.close()
    log(f"\n=== TOTAL: +{total_lrc}LRC +{total_txt}TXT, {total_miss}miss ===")
    
    # Final coverage
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM tracks')
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM tracks WHERE (lyrics_text_path IS NOT NULL AND lyrics_text_path != '') OR (lyrics_lrc_path IS NOT NULL AND lyrics_lrc_path != '')")
    has = c.fetchone()[0]
    log(f"Coverage: {has}/{total} = {has/total*100:.1f}%")
    conn.close()

if __name__ == '__main__':
    main()
