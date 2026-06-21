# -*- coding: utf-8 -*-
"""
批量补全缺歌词 - 分批版（每批50首）
用法：python _lyrics_batch.py 1   # 处理第1批（1-50）
      python _lyrics_batch.py 2   # 处理第2批（51-100）
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

def log(msg):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

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
        log(f"ERROR: {e}")
    return None, None

def main():
    batch_num = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    offset = (batch_num - 1) * 50

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
    SELECT t.id, t.album_id, t.track_name, a.artist, a.album_name
    FROM tracks t
    JOIN albums a ON t.album_id = a.album_id
    WHERE t.lyrics_lrc_path IS NULL AND t.lyrics_text_path IS NULL
    ORDER BY t.album_id, t.track_number
    LIMIT 50 OFFSET ?
    ''', (offset,))
    tracks = c.fetchall()

    log(f"\n=== Batch {batch_num} (offset {offset}) ===")
    log(f"Processing {len(tracks)} tracks")

    success = 0
    for i, (track_id, album_id, track_name, artist, album_name) in enumerate(tracks):
        log(f"[{i+1}/{len(tracks)}] {artist} - {track_name}")

        lrc, txt = search_lrclib(artist, track_name)

        if lrc or txt:
            artist_safe = artist.replace('/', '_').replace('\\', '_') if artist else 'Unknown'
            album_safe = album_name.replace('/', '_').replace('\\', '_') if album_name else 'Unknown'

            artist_dir = os.path.join(LYRICS_DIR, artist_safe)
            os.makedirs(artist_dir, exist_ok=True)
            album_dir = os.path.join(artist_dir, album_safe)
            os.makedirs(album_dir, exist_ok=True)

            c2 = conn.cursor()
            c2.execute('SELECT track_number FROM tracks WHERE id = ?', (track_id,))
            row = c2.fetchone()
            track_num = row[0] if row else 1

            if lrc:
                lrc_file = os.path.join(album_dir, f"{track_num:02d}.lrc")
                with open(lrc_file, 'w', encoding='utf-8') as f:
                    f.write(lrc)
                lrc_path = lrc_file.replace(LYRICS_DIR, '').replace('\\', '/').lstrip('/')
                c.execute('UPDATE tracks SET lyrics_lrc_path = ? WHERE id = ?', (lrc_path, track_id))
                log(f"  -> LRC saved")
                success += 1

            if txt:
                txt_file = os.path.join(album_dir, f"{track_num:02d}.txt")
                with open(txt_file, 'w', encoding='utf-8') as f:
                    f.write(txt)
                txt_path = txt_file.replace(LYRICS_DIR, '').replace('\\', '/').lstrip('/')
                c.execute('UPDATE tracks SET lyrics_text_path = ? WHERE id = ?', (txt_path, track_id))
                if not lrc:
                    log(f"  -> TXT saved")
                    success += 1

            conn.commit()
        else:
            log(f"  -> NOT FOUND")

        time.sleep(0.3)

    conn.close()
    log(f"Batch {batch_num} done! Success: {success}/{len(tracks)}")
    print(f"Batch {batch_num} done! Success: {success}/{len(tracks)}")

if __name__ == '__main__':
    main()
