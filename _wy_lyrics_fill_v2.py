#!/usr/bin/env python3
"""
_wy_lyrics_fill_v2.py - 网易云歌词批量获取 + 数据库回填 v3
改进：
1. 专辑API返回0歌曲时，fallback到歌曲搜索（type=1）
2. 从搜索结果中提取歌曲，逐首获取歌词
3. 直接更新 tracks 表
"""
import sqlite3, os, json, time, urllib.request, urllib.parse, re, sys

DB = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"
LYRICS_ROOT = r"C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics"
WY_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://music.163.com"
}
DELAY = 0.8

def norm(s):
    return re.sub(r'[\s\-_\.\(\)\[\]\{\}\,\!\?\:\;\'\"\/\\]', '', s).lower()

def safe_fn(s):
    return re.sub(r'[<>:"/\\|?*]', '', s).strip() or "unknown"

def has_chinese(s):
    return any('\u4e00' <= c <= '\u9fff' for c in s)

def fetch(url):
    req = urllib.request.Request(url, headers=WY_HEADERS)
    resp = urllib.request.urlopen(req, timeout=15)
    return json.loads(resp.read())

def search_album(artist, album):
    """搜索网易云专辑"""
    q = f"{artist} {album}"
    url = f"https://music.163.com/api/search/get?s={urllib.parse.quote(q)}&type=10&limit=20"
    try:
        data = fetch(url)
        albums = data.get("result", {}).get("albums", [])
    except:
        return None, None
    if not albums:
        return None, None
    album_norm = norm(album)
    for al in albums:
        al_name = al.get("name", "")
        al_norm = norm(al_name)
        if album_norm == al_norm or album_norm in al_norm or al_norm in album_norm:
            return al["id"], al_name
    return albums[0]["id"], albums[0].get("name", "")

def get_songs_from_album(album_id):
    """专辑API获取曲目"""
    url = f"https://music.163.com/api/album/{album_id}"
    try:
        data = fetch(url)
        songs = data.get("album", {}).get("songs", [])
        if songs:
            return [{"id": s["id"], "name": s["name"]} for s in songs]
    except:
        pass
    return None

def get_songs_from_search(artist, album):
    """搜索歌曲方式获取曲目（fallback）"""
    q = f"{artist} {album}"
    url = f"https://music.163.com/api/search/get?s={urllib.parse.quote(q)}&type=1&limit=50"
    try:
        data = fetch(url)
        songs = data.get("result", {}).get("songs", [])
    except:
        return None

    # 过滤：只保留专辑名匹配的
    album_norm = norm(album)
    filtered = []
    seen_ids = set()
    for s in songs:
        if s["id"] in seen_ids:
            continue
        al = s.get("album", {}) or {}
        al_name = al.get("name", "") if isinstance(al, dict) else ""
        al_norm = norm(al_name)
        if album_norm == al_norm or album_norm in al_norm or al_norm in album_norm:
            filtered.append({"id": s["id"], "name": s["name"]})
            seen_ids.add(s["id"])

    return filtered if filtered else None

def get_lyric(song_id):
    """获取歌词"""
    url = f"https://music.163.com/api/song/lyric?id={song_id}&lv=1&tv=1"
    try:
        data = fetch(url)
        lrc = data.get("lrc", {}).get("lyric", "") or ""
        trans = data.get("tlyric", {}).get("lyric", "") or ""
        return lrc, trans
    except:
        return "", ""

def parse_lrc_to_text(lrc_text):
    lines = []
    for line in lrc_text.split("\n"):
        clean = re.sub(r"\[\d+:\d+\.\d+\]", "", line).strip()
        if clean and not clean.startswith("["):
            lines.append(clean)
    return "\n".join(lines)

def match_track(track_name, db_tracks):
    """匹配网易云曲目到数据库曲目"""
    tn = norm(track_name)
    for dt in db_tracks:
        if norm(dt["track_name"]) == tn:
            return dt
    # 前缀
    for dt in db_tracks:
        dn = norm(dt["track_name"])
        if len(tn) >= 4 and (tn[:8] in dn[:8] or dn[:8] in tn[:8]):
            return dt
    return None

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    db = sqlite3.connect(DB, timeout=30)
    db.row_factory = sqlite3.Row

    albums = db.execute("""
        SELECT a.album_id, a.artist, a.album_name,
               COUNT(lh.id) as listen_cnt
        FROM albums a
        JOIN tracks t ON t.album_id = a.album_id
        LEFT JOIN listen_history lh ON lh.album_id = a.album_id
        WHERE (t.lyrics_text_path IS NULL AND t.lyrics_lrc_path IS NULL)
        GROUP BY a.album_id
        ORDER BY listen_cnt DESC
    """).fetchall()

    cn = [a for a in albums if has_chinese(a["artist"]) or has_chinese(a["album_name"])]
    print(f"缺歌词中文专辑: {len(cn)}", flush=True)

    total_ok = 0
    total_fail = 0

    for album in cn[:15]:
        aid = album["album_id"]
        artist = album["artist"]
        album_name = album["album_name"]

        print(f"\n{artist} - {album_name} (id={aid})", flush=True)

        # 搜索
        wy_id, wy_name = search_album(artist, album_name)
        if not wy_id:
            print(f"  Not found on WY", flush=True)
            total_fail += 1
            continue

        time.sleep(DELAY)

        # 获取曲目：先专辑API，失败则搜索
        songs = get_songs_from_album(wy_id)
        source = "album_api"
        if not songs:
            songs = get_songs_from_search(artist, album_name)
            source = "search"
        
        if not songs:
            print(f"  No songs via any method", flush=True)
            total_fail += 1
            continue

        print(f"  {wy_name}: {len(songs)} songs ({source})", flush=True)
        time.sleep(DELAY)

        # 数据库曲目
        db_tracks = [dict(r) for r in db.execute(
            "SELECT id, track_number, track_name FROM tracks WHERE album_id = ? AND lyrics_text_path IS NULL AND lyrics_lrc_path IS NULL",
            (aid,)
        ).fetchall()]

        save_dir = os.path.join(LYRICS_ROOT, safe_fn(artist), safe_fn(album_name))
        os.makedirs(save_dir, exist_ok=True)

        found = 0
        for song in songs:
            lrc, trans = get_lyric(song["id"])
            if not lrc:
                time.sleep(DELAY)
                continue

            tname = safe_fn(song["name"])
            txt_path = os.path.join(save_dir, f"{tname}.txt")
            lrc_path = os.path.join(save_dir, f"{tname}.lrc")

            plain = parse_lrc_to_text(lrc)
            if plain:
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(plain)
            with open(lrc_path, "w", encoding="utf-8") as f:
                f.write(lrc)

            # 翻译
            if trans:
                trans_path = os.path.join(save_dir, f"{tname}_zh.lrc")
                with open(trans_path, "w", encoding="utf-8") as f:
                    f.write(trans)

            # 匹配数据库
            matched = match_track(song["name"], db_tracks)
            if matched:
                db.execute(
                    "UPDATE tracks SET lyrics_text_path=?, lyrics_lrc_path=? WHERE id=?",
                    (txt_path, lrc_path, matched["id"])
                )
                db_tracks.remove(matched)
                found += 1

            time.sleep(DELAY)

        db.commit()
        print(f"  Lyrics: {found}/{len(db_tracks) + found}", flush=True)
        total_ok += found

    print(f"\nDone. OK={total_ok} FAIL={total_fail}", flush=True)
    db.close()

if __name__ == "__main__":
    main()
