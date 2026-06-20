#!/usr/bin/env python3
# _lyrics_test_lrclib.py - 测试 LRCLIB 批量抓取（前5张专辑）
import sqlite3, os, json, time, urllib.request, urllib.parse, re, sys

DB = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"
LYRICS_ROOT = r"C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics"
LRCLIB_API = "https://lrclib.net/api/search"

def norm(s):
    return re.sub(r'[\s\-_\.\(\)\[\]\{\}\,\!\?\:\;\'\"\/\\]', '', s).lower()

def safe_filename(s):
    return re.sub(r'[<>:"/\\|?*]', '', s).strip()

def search_lrclib(artist, track, album=""):
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
            score += 2
        if item.get('plainLyrics'):
            score += 1
        if score > best_score:
            best_score = score
            best = item

    return best if best and best_score >= 5 else None

db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row

albums = db.execute('''
    SELECT a.album_id, a.artist, a.album_name,
           COUNT(lh.id) as listen_cnt
    FROM albums a
    JOIN tracks t ON t.album_id = a.album_id
    LEFT JOIN listen_history lh ON lh.album_id = a.album_id
    WHERE t.lyrics_text_path IS NULL AND t.lyrics_lrc_path IS NULL
    GROUP BY a.album_id
    ORDER BY listen_cnt DESC
    LIMIT 5
''').fetchall()

print(f"Test: {len(albums)} albums", flush=True)
sys.stdout.reconfigure(encoding='utf-8')

total_found = 0
for album in albums:
    aid = album['album_id']
    artist = album['artist']
    album_name = album['album_name']

    tracks = db.execute(
        'SELECT id, track_number, track_name FROM tracks WHERE album_id = ? ORDER BY track_number',
        (aid,)
    ).fetchall()

    print(f"\n{artist} - {album_name} ({len(tracks)} tracks)", flush=True)

    artist_dir = os.path.join(LYRICS_ROOT, safe_filename(artist))
    save_dir = os.path.join(artist_dir, safe_filename(album_name) or f"album_{aid}")
    os.makedirs(save_dir, exist_ok=True)

    found = 0
    for track in tracks:
        result = search_lrclib(artist, track['track_name'], album_name)
        if not result:
            continue
        plain = result.get('plainLyrics')
        synced = result.get('syncedLyrics')
        if not plain and not synced:
            continue

        tname = safe_filename(track['track_name']) or f"track_{track['track_number']}"
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
        total_found += 1
        time.sleep(0.5)

    print(f"  Found: {found}/{len(tracks)}", flush=True)
    db.commit()

print(f"\nTotal found: {total_found}", flush=True)
db.close()
