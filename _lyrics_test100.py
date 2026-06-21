# -*- coding: utf-8 -*-
"""
批量补全缺歌词 - 测试版（前100首）
"""

import sqlite3
import urllib.request
import urllib.parse
import json
import time
import os

DB_PATH = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
LYRICS_DIR = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics'

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
        pass
    return None, None

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
    SELECT t.id, t.album_id, t.track_name, a.artist, a.album_name
    FROM tracks t
    JOIN albums a ON t.album_id = a.album_id
    WHERE t.lyrics_lrc_path IS NULL AND t.lyrics_text_path IS NULL
    ORDER BY t.album_id, t.track_number
    LIMIT 100
    ''')
    tracks = c.fetchall()

    print(f"Processing {len(tracks)} tracks...")

    success = 0
    for i, (track_id, album_id, track_name, artist, album_name) in enumerate(tracks):
        lrc, txt = search_lrclib(artist, track_name)

        if lrc or txt:
            # 保存文件
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
                success += 1

            if txt:
                txt_file = os.path.join(album_dir, f"{track_num:02d}.txt")
                with open(txt_file, 'w', encoding='utf-8') as f:
                    f.write(txt)
                txt_path = txt_file.replace(LYRICS_DIR, '').replace('\\', '/').lstrip('/')
                c.execute('UPDATE tracks SET lyrics_text_path = ? WHERE id = ?', (txt_path, track_id))
                if not lrc:
                    success += 1

            conn.commit()

        # 每10首报告
        if (i + 1) % 10 == 0:
            print(f"Progress: {i+1}/100 | Success: {success}")

        time.sleep(0.5)

    conn.close()
    print(f"\nDone! Success: {success}/100")

if __name__ == '__main__':
    main()
