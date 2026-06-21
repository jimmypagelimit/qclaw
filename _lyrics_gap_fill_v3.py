# -*- coding: utf-8 -*-
"""
批量补全缺歌词专辑
- 英文专辑：LRCLIB API
- 中文专辑：网易云 API（需要手动实现，这里先跑 LRCLIB）
"""

import sqlite3
import urllib.request
import json
import time
import os

DB_PATH = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
LYRICS_DIR = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics'

def search_lrclib(artist, track_name):
    """搜索 LRCLIB 歌词"""
    # URL encode the query
    import urllib.parse
    query = f"{artist} {track_name}"
    query_encoded = urllib.parse.quote(query)
    url = f"https://lrclib.net/api/search?q={query_encoded}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode())
        if data and len(data) > 0:
            # 优先选有 syncedLyrics 的
            for item in data:
                if item.get('syncedLyrics'):
                    return item['syncedLyrics'], item.get('plainLyrics', '')
            # 没有同步歌词，用纯文本
            if data[0].get('plainLyrics'):
                return None, data[0]['plainLyrics']
    except Exception as e:
        print(f"  LRCLIB error: {e}")
    return None, None

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 获取缺歌词的曲目
    c.execute('''
    SELECT t.id, t.album_id, t.track_name, a.artist, a.album_name
    FROM tracks t
    JOIN albums a ON t.album_id = a.album_id
    WHERE t.lyrics_lrc_path IS NULL AND t.lyrics_text_path IS NULL
    ORDER BY t.album_id, t.track_number
    ''')
    tracks = c.fetchall()

    print(f"Total tracks missing lyrics: {len(tracks)}")

    success = 0
    fail = 0
    current_album = None

    for i, (track_id, album_id, track_name, artist, album_name) in enumerate(tracks):
        if album_id != current_album:
            current_album = album_id
            print(f"\n[{album_id}] {repr(artist)} - {repr(album_name)}")

        # 搜索 LRCLIB
        lrc, txt = search_lrclib(artist, track_name)

        if lrc or txt:
            # 保存文件
            artist_dir = os.path.join(LYRICS_DIR, artist.replace('/', '_'))
            os.makedirs(artist_dir, exist_ok=True)

            album_dir = os.path.join(artist_dir, album_name.replace('/', '_'))
            os.makedirs(album_dir, exist_ok=True)

            # 文件名：track_number.track_name.lrc/txt
            c2 = conn.cursor()
            c2.execute('SELECT track_number FROM tracks WHERE id = ?', (track_id,))
            track_num = c2.fetchone()[0]

            if lrc:
                lrc_file = os.path.join(album_dir, f"{track_num:02d}.{track_name}.lrc")
                with open(lrc_file, 'w', encoding='utf-8') as f:
                    f.write(lrc)
                lrc_path = lrc_file.replace(LYRICS_DIR, '').replace('\\', '/').lstrip('/')
                c.execute('UPDATE tracks SET lyrics_lrc_path = ? WHERE id = ?', (lrc_path, track_id))
                print(f"  OK {track_num:02d}. {repr(track_name)} [LRC]")
                success += 1

            if txt:
                txt_file = os.path.join(album_dir, f"{track_num:02d}.{track_name}.txt")
                with open(txt_file, 'w', encoding='utf-8') as f:
                    f.write(txt)
                txt_path = txt_file.replace(LYRICS_DIR, '').replace('\\', '/').lstrip('/')
                c.execute('UPDATE tracks SET lyrics_text_path = ? WHERE id = ?', (txt_path, track_id))
                if not lrc:
                    print(f"  OK {track_num:02d}. {repr(track_name)} [TXT]")
                success += 1

            conn.commit()
        else:
            fail += 1
            # print(f"  FAIL {repr(track_name)}")  # skip print to avoid GBK error

        # 限流
        time.sleep(0.3)

        # 每50首报告进度
        if (i + 1) % 50 == 0:
            print(f"\n--- Progress: {i+1}/{len(tracks)} | Success: {success} | Fail: {fail} ---\n")

    conn.close()
    print(f"\n=== Done ===")
    print(f"Success: {success}")
    print(f"Fail: {fail}")

if __name__ == '__main__':
    main()
