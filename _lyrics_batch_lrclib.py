#!/usr/bin/env python3
# _lyrics_batch_lrclib.py - 批量从 LRCLIB 获取歌词
# 策略：对缺歌词专辑，按收听次数降序，逐张抓取 LRCLIB 歌词
import sqlite3, os, json, time, urllib.request, urllib.parse, re

DB = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"
LYRICS_ROOT = r"C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics"
LRCLIB_API = "https://lrclib.net/api/search"

def norm(s):
    return re.sub(r'[\s\-_\.\(\)\[\]\{\}\,\!\?\:\;\'\"\/\\]', '', s).lower()

def safe_filename(s):
    """文件名安全化"""
    return re.sub(r'[<>:"/\\|?*]', '', s).strip()

def search_lrclib(artist, track, album=""):
    """搜索 LRCLIB，返回最佳匹配"""
    q = f"{artist} {track}"
    url = f"{LRCLIB_API}?q={urllib.parse.quote(q)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        return None

    if not data:
        return None

    # 找最佳匹配：track名匹配 + album匹配加分
    best = None
    best_score = -1
    track_norm = norm(track)
    artist_norm = norm(artist)
    album_norm = norm(album) if album else ""

    for item in data:
        score = 0
        if norm(item.get('trackName', '')) == track_norm:
            score += 10
        if artist_norm in norm(item.get('artistName', '')):
            score += 5
        if album_norm and norm(item.get('albumName', '')) == album_norm:
            score += 3
        if item.get('syncedLyrics'):
            score += 2  # 优先有同步歌词
        if item.get('plainLyrics'):
            score += 1
        if score > best_score:
            best_score = score
            best = item

    return best if best and best_score >= 5 else None

def main():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row

    # 找缺歌词的专辑（有曲目但无歌词路径），按收听次数降序
    albums = db.execute('''
        SELECT a.album_id, a.artist, a.album_name,
               COUNT(lh.id) as listen_cnt,
               COUNT(t.id) as track_cnt,
               SUM(CASE WHEN t.lyrics_text_path IS NOT NULL OR t.lyrics_lrc_path IS NOT NULL THEN 1 ELSE 0 END) as has_lyrics_cnt
        FROM albums a
        JOIN tracks t ON t.album_id = a.album_id
        LEFT JOIN listen_history lh ON lh.album_id = a.album_id
        WHERE t.lyrics_text_path IS NULL AND t.lyrics_lrc_path IS NULL
        GROUP BY a.album_id
        HAVING has_lyrics_cnt = 0
        ORDER BY listen_cnt DESC, track_cnt DESC
    ''').fetchall()

    print(f"缺歌词专辑: {len(albums)}")

    # 按艺人分组统计
    artist_stats = {}
    for a in albums:
        an = a['artist']
        if an not in artist_stats:
            artist_stats[an] = {'count': 0, 'listen': 0}
        artist_stats[an]['count'] += 1
        artist_stats[an]['listen'] += a['listen_cnt']

    print("\n--- 按艺人统计 (Top 15) ---")
    for an, s in sorted(artist_stats.items(), key=lambda x: x[1]['listen'], reverse=True)[:15]:
        print(f"  {an}: {s['count']} albums, {s['listen']} listens")

    # 开始批量抓取
    total_found = 0
    total_tracks = 0
    errors = 0

    for i, album in enumerate(albums):
        aid = album['album_id']
        artist = album['artist']
        album_name = album['album_name']
        listen_cnt = album['listen_cnt']

        # 获取该专辑的曲目
        tracks = db.execute(
            'SELECT id, track_number, track_name FROM tracks WHERE album_id = ? ORDER BY track_number',
            (aid,)
        ).fetchall()

        print(f"\n[{i+1}/{len(albums)}] {artist} - {album_name} (listens={listen_cnt}, tracks={len(tracks)})")

        # 创建歌词目录
        artist_dir = os.path.join(LYRICS_ROOT, safe_filename(artist))
        album_dir_name = safe_filename(album_name)
        if not album_dir_name:
            album_dir_name = f"album_{aid}"
        save_dir = os.path.join(artist_dir, album_dir_name)
        os.makedirs(save_dir, exist_ok=True)

        album_found = 0
        for track in tracks:
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

            # 保存文件
            tname_safe = safe_filename(tname)
            if not tname_safe:
                tname_safe = f"track_{tnum}"

            txt_path = None
            lrc_path = None

            if plain:
                txt_path = os.path.join(save_dir, f"{tname_safe}.txt")
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(plain)
            if synced:
                lrc_path = os.path.join(save_dir, f"{tname_safe}.lrc")
                with open(lrc_path, 'w', encoding='utf-8') as f:
                    f.write(synced)

            # 更新数据库
            db.execute(
                "UPDATE tracks SET lyrics_text_path=?, lyrics_lrc_path=? WHERE id=?",
                (txt_path, lrc_path, tid)
            )
            album_found += 1
            total_found += 1

            # 限流
            time.sleep(0.5)

        total_tracks += len(tracks)
        if album_found > 0:
            print(f"  Found {album_found}/{len(tracks)} tracks with lyrics")
        else:
            # 删除空目录
            if not os.listdir(save_dir):
                os.rmdir(save_dir)
            if os.path.exists(artist_dir) and not os.listdir(artist_dir):
                os.rmdir(artist_dir)

        db.commit()

        # 每处理10张专辑输出一次进度
        if (i + 1) % 10 == 0:
            print(f"\n=== Progress: {i+1}/{len(albums)} albums, {total_found} lyrics found ===\n")

    db.commit()
    print(f"\nDone! Total: {total_found} lyrics found for {total_tracks} tracks in {len(albums)} albums")
    db.close()

if __name__ == '__main__':
    main()
