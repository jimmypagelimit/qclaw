#!/usr/bin/env python3
"""
歌词计划 cron 批量抓取
- 目标：高知名度艺人 + 高收听量专辑
- 策略：LRCLIB API 查询
- 时间限制：65秒（留余量给SIGKILL）
"""
import sqlite3, os, json, time, urllib.request, urllib.parse, re, sys

DB = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"
LRCLIB_API = "https://lrclib.net/api/search"
TIME_LIMIT = 65  # 秒

START_TIME = time.time()

def norm(s):
    return re.sub(r'[\s\-_\.\(\)\[\]\{\}\,\!\?\:\;\'\"\/\\]', '', s or '').lower()

def safe_fn(s):
    return re.sub(r'[<>:"/\\|?*]', '', s or '').strip() or 'untitled'

def get_elapsed():
    return time.time() - START_TIME

def log(msg):
    elapsed = get_elapsed()
    print(f"[{elapsed:.1f}s] {msg}", flush=True)

def check_time():
    if get_elapsed() > TIME_LIMIT:
        log("TIME LIMIT REACHED, exiting gracefully")
        return False
    return True

def search_lrclib(artist, track, album=""):
    q = f"{artist} {track}"
    url = f"{LRCLIB_API}?q={urllib.parse.quote(q)}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode('utf-8'))
    except Exception:
        return None

    if not data:
        return None

    track_norm = norm(track)
    artist_norm = norm(artist)
    album_norm = norm(album) if album else ""

    best, best_score = None, -1
    for item in data:
        score = 0
        if norm(item.get('trackName', '')) == track_norm:
            score += 10
        if artist_norm in norm(item.get('artistName', '')):
            score += 5
        if album_norm and norm(item.get('albumName', '')) == album_norm:
            score += 3
        if item.get('syncedLyrics'):
            score += 2
        if item.get('plainLyrics'):
            score += 1
        if score > best_score:
            best_score = score
            best = item

    return best if best and best_score >= 5 else None

def main():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row

    # 获取缺歌词曲目，按专辑收听次数降序（取 Top 500）
    tracks = db.execute('''
        SELECT t.id, t.track_name, t.track_number, t.album_id,
               a.artist, a.album_name,
               COALESCE(lh.cnt, 0) as listen_cnt,
               t.lyrics_text_path, t.lyrics_lrc_path
        FROM tracks t
        JOIN albums a ON t.album_id = a.album_id
        LEFT JOIN (
            SELECT album_id, COUNT(*) as cnt
            FROM listen_history GROUP BY album_id
        ) lh ON lh.album_id = t.album_id
        WHERE t.lyrics_text_path IS NULL AND t.lyrics_lrc_path IS NULL
        ORDER BY listen_cnt DESC, a.album_id
        LIMIT 200
    ''').fetchall()

    log(f"缺歌词曲目: {len(tracks)}")

    if not tracks:
        db.close()
        return

    # 统计Top艺人
    artist_counts = {}
    for t in tracks:
        ar = t['artist']
        artist_counts[ar] = artist_counts.get(ar, 0) + 1

    log(f"Top 艺人对缺歌词贡献: {sorted(artist_counts.items(), key=lambda x: -x[1])[:10]}")

    total_found = 0
    total_tried = 0
    errors = 0

    # 确保歌词目录存在
    LYRICS_ROOT = r"C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics"
    os.makedirs(LYRICS_ROOT, exist_ok=True)

    for i, track in enumerate(tracks):
        if not check_time():
            break

        tid = track['id']
        artist = track['artist']
        album_name = track['album_name']
        track_name = track['track_name']
        track_num = track['track_number']
        aid = track['album_id']

        total_tried += 1
        log(f"[{i+1}/{len(tracks)}] {artist} - {track_name}")

        result = search_lrclib(artist, track_name, album_name)
        if not result:
            errors += 1
            time.sleep(0.3)
            continue

        plain = result.get('plainLyrics')
        synced = result.get('syncedLyrics')
        if not plain and not synced:
            errors += 1
            time.sleep(0.3)
            continue

        # 保存文件
        artist_dir = os.path.join(LYRICS_ROOT, safe_fn(artist))
        album_dir = os.path.join(artist_dir, safe_fn(album_name) or f"album_{aid}")
        os.makedirs(album_dir, exist_ok=True)

        tname_safe = safe_fn(track_name) or f"track_{track_num}"

        txt_path = None
        lrc_path = None

        if plain:
            txt_path = os.path.join(album_dir, f"{tname_safe}.txt")
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(plain)

        if synced:
            lrc_path = os.path.join(album_dir, f"{tname_safe}.lrc")
            with open(lrc_path, 'w', encoding='utf-8') as f:
                f.write(synced)

        db.execute(
            "UPDATE tracks SET lyrics_text_path=?, lyrics_lrc_path=? WHERE id=?",
            (txt_path, lrc_path, tid)
        )
        total_found += 1
        log(f"  ✓ Found lyrics: {result.get('albumName','')} / {result.get('trackName','')}")

        time.sleep(0.4)

    db.commit()
    log(f"\n完成! 尝试: {total_tried}, 成功: {total_found}, 失败: {errors}")
    db.close()

if __name__ == '__main__':
    main()
