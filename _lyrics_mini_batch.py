# -*- coding: utf-8 -*-
"""
歌词计划迷你批次 - 每次只处理少量专辑，确保<60秒完成
"""
import sqlite3, os, json, time, urllib.request, urllib.parse, re

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
LYRICS_ROOT = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics'
LRCLIB_API = 'https://lrclib.net/api/search'
BATCH_LIMIT = 15  # 每次最多处理专辑数
MAX_TIME = 55      # 最大耗时秒

def norm(s):
    return re.sub(r'[\s\-_.\(\)\[\]{}\,\!\?\:\;\'"\\/]', '', str(s)).lower()

def safe_fn(s):
    return re.sub(r'[<>:"/\\|?*]', '', s).strip() or 'untitled'

def search_lrclib(artist, track, album=''):
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

    track_n = norm(track)
    artist_n = norm(artist)
    album_n = norm(album) if album else ''
    best, best_score = None, -1
    for item in data:
        score = 0
        if norm(item.get('trackName','')) == track_n:
            score += 10
        if artist_n in norm(item.get('artistName','')):
            score += 5
        if album_n and norm(item.get('albumName','')) == album_n:
            score += 3
        if item.get('syncedLyrics'):
            score += 2
        if item.get('plainLyrics'):
            score += 1
        if score > best_score:
            best_score, best = score, item
    return best if best and best_score >= 5 else None

def main():
    start = time.time()
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row

    # 取缺歌词专辑，随机取BATCH_LIMIT张（先测英文/独立音乐，成功率高）
    albums = db.execute('''
        SELECT a.album_id, a.artist, a.album_name,
               COUNT(t.id) as track_cnt
        FROM albums a
        JOIN tracks t ON t.album_id = a.album_id
        WHERE t.lyrics_text_path IS NULL AND t.lyrics_lrc_path IS NULL
        GROUP BY a.album_id
        HAVING COUNT(t.id) > 0
        ORDER BY RANDOM()
        LIMIT ?
    ''', (BATCH_LIMIT,)).fetchall()

    if not albums:
        print('没有缺歌词的专辑了')
        db.close()
        return

    print(f'处理 {len(albums)} 张专辑...')
    total_found = 0
    total_tracks = 0

    for album in albums:
        if time.time() - start > MAX_TIME:
            print(f'达到时间限制，停止')
            break

        aid = album['album_id']
        artist = album['artist']
        album_name = album['album_name']
        tracks = db.execute(
            'SELECT id, track_number, track_name FROM tracks WHERE album_id=? ORDER BY track_number',
            (aid,)
        ).fetchall()

        print(f'  {artist} - {album_name} ({len(tracks)}首)')
        album_found = 0

        for track in tracks:
            if time.time() - start > MAX_TIME:
                break
            tid = track['id']
            tnum = track['track_number']
            tname = track['track_name']

            result = search_lrclib(artist, tname, album_name)
            if not result:
                continue

            plain = result.get('plainLyrics')
            synced = result.get('syncedLyrics')
            if not plain and not synced:
                continue

            tname_safe = safe_fn(tname) or f'track_{tnum}'
            artist_dir = os.path.join(LYRICS_ROOT, safe_fn(artist))
            album_dir = os.path.join(artist_dir, safe_fn(album_name) or f'album_{aid}')
            os.makedirs(album_dir, exist_ok=True)

            txt_path = lrc_path = None
            if plain:
                txt_path = os.path.join(album_dir, f'{tname_safe}.txt')
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(plain)
            if synced:
                lrc_path = os.path.join(album_dir, f'{tname_safe}.lrc')
                with open(lrc_path, 'w', encoding='utf-8') as f:
                    f.write(synced)

            db.execute(
                "UPDATE tracks SET lyrics_text_path=?, lyrics_lrc_path=? WHERE id=?",
                (txt_path, lrc_path, tid)
            )
            album_found += 1
            total_found += 1
            time.sleep(0.4)

        total_tracks += len(tracks)
        db.commit()
        print(f'    -> 找到 {album_found}/{len(tracks)} 首')

    db.commit()

    # 统计
    total = db.execute('SELECT COUNT(*) FROM tracks').fetchone()[0]
    with_lyrics = db.execute('SELECT COUNT(*) FROM tracks WHERE lyrics_text_path IS NOT NULL OR lyrics_lrc_path IS NOT NULL').fetchone()[0]
    with_lrc = db.execute('SELECT COUNT(*) FROM tracks WHERE lyrics_lrc_path IS NOT NULL').fetchone()[0]
    elapsed = time.time() - start

    print(f'\n完成！耗时 {elapsed:.1f}秒')
    print(f'本次找到 {total_found} 首歌词')
    print(f'总进度: {with_lyrics}/{total} ({with_lyrics*100/total:.1f}%) 有歌词, {with_lrc*100/total:.1f}% 有LRC')
    db.close()

if __name__ == '__main__':
    main()
