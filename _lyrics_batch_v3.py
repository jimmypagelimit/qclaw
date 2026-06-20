#!/usr/bin/env python3
# _lyrics_batch_v3.py - LRCLIB 歌词获取 v3
# 策略：曲目少的优先，单首专辑先行，10张/轮
import sqlite3, os, json, time, urllib.request, urllib.parse, re, sys

DB = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"
LYRICS_ROOT = r"C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics"
LRCLIB_API = "https://lrclib.net/api/search"
BATCH = 30

def norm(s):
    return re.sub(r'[\s\-_\.\(\)\[\]\{\}\,\!\?\:\;\'\"\/\\]', '', s).lower()

def safe_fn(s):
    return re.sub(r'[<>:"/\\|?*]', '', s).strip() or "unknown"

def search_lrclib(artist, track):
    q = f"{artist} {track}"
    url = f"{LRCLIB_API}?q={urllib.parse.quote(q)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode('utf-8'))
    except:
        return None
    if not data:
        return None
    item = data[0]
    if norm(item.get('trackName', '')) == norm(track) and norm(artist) in norm(item.get('artistName', '')):
        return item
    return None

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    db = sqlite3.connect(DB, timeout=30)
    db.row_factory = sqlite3.Row

    # 英文专辑，曲目少的优先
    albums = db.execute('''
        SELECT a.album_id, a.artist, a.album_name,
               COUNT(lh.id) as listen_cnt,
               SUM(CASE WHEN t.lyrics_text_path IS NULL AND t.lyrics_lrc_path IS NULL THEN 1 ELSE 0 END) as missing
        FROM albums a
        JOIN tracks t ON t.album_id = a.album_id
        LEFT JOIN listen_history lh ON lh.album_id = a.album_id
        WHERE (t.lyrics_text_path IS NULL AND t.lyrics_lrc_path IS NULL)
        GROUP BY a.album_id
        HAVING missing > 0
        ORDER BY missing ASC
    ''').fetchall()

    # 过滤英文
    en = [a for a in albums if not any(0x4e00 <= ord(c) <= 0x9fff for c in a['artist'])]
    batch = en[:BATCH]

    print(f"缺歌词英文专辑: {len(en)}, 本批: {len(batch)}", flush=True)

    total = 0
    for album in batch:
        aid = album['album_id']
        artist = album['artist']
        album_name = album['album_name']

        tracks = db.execute(
            'SELECT id, track_number, track_name FROM tracks WHERE album_id = ? AND lyrics_text_path IS NULL AND lyrics_lrc_path IS NULL',
            (aid,)
        ).fetchall()

        print(f"\n{artist} - {album_name} ({len(tracks)} missing)", flush=True)

        save_dir = os.path.join(LYRICS_ROOT, safe_fn(artist), safe_fn(album_name))
        os.makedirs(save_dir, exist_ok=True)

        found = 0
        for track in tracks:
            result = search_lrclib(artist, track['track_name'])
            if not result:
                continue
            plain = result.get('plainLyrics')
            synced = result.get('syncedLyrics')
            if not plain and not synced:
                continue

            tname = safe_fn(track['track_name'])
            txt_path = lrc_path = None
            if plain:
                txt_path = os.path.join(save_dir, f"{tname}.txt")
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(plain)
            if synced:
                lrc_path = os.path.join(save_dir, f"{tname}.lrc")
                with open(lrc_path, 'w', encoding='utf-8') as f:
                    f.write(synced)

            db.execute("UPDATE tracks SET lyrics_text_path=?, lyrics_lrc_path=? WHERE id=?",
                       (txt_path, lrc_path, track['id']))
            found += 1
            total += 1
            time.sleep(0.3)

        print(f"  Found: {found}/{len(tracks)}", flush=True)
        db.commit()

    print(f"\nDone. Total: {total}", flush=True)
    db.close()

if __name__ == '__main__':
    main()
