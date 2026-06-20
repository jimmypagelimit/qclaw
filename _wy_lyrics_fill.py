#!/usr/bin/env python3
"""
_wy_lyrics_fill.py - 网易云歌词批量获取 + 数据库回填 v2
改进：
1. 搜索匹配更精确（专辑名模糊匹配 + artist过滤）
2. 抓取后直接更新 tracks 表的 lyrics_text_path / lyrics_lrc_path
3. 只处理缺歌词的中文专辑
4. 按 listen_cnt 降序优先
"""
import sqlite3, os, json, time, urllib.request, urllib.parse, re, sys

DB = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"
LYRICS_ROOT = r"C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics"
WY_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://music.163.com"
}
DELAY = 0.8  # API 请求间隔

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
    """搜索网易云专辑，返回 (id, name) 或 None"""
    q = f"{artist} {album}"
    # 搜索专辑 (type=10)
    url = f"https://music.163.com/api/search/get?s={urllib.parse.quote(q)}&type=10&limit=20"
    try:
        data = fetch(url)
        albums = data.get("result", {}).get("albums", [])
    except:
        return None, None

    if not albums:
        return None, None

    # 最佳匹配：专辑名精确/包含匹配
    album_norm = norm(album)
    for al in albums:
        al_name = al.get("name", "")
        al_norm = norm(al_name)
        if album_norm == al_norm or album_norm in al_norm or al_norm in album_norm:
            return al["id"], al_name

    # 没匹配上取第一个
    return albums[0]["id"], albums[0].get("name", "")

def get_album_songs(album_id):
    """获取专辑曲目列表"""
    url = f"https://music.163.com/api/album/{album_id}"
    try:
        data = fetch(url)
        if data.get("code") == 200:
            songs = data.get("album", {}).get("songs", [])
            if songs:
                return [{"id": s["id"], "name": s["name"], "no": s.get("no", i+1)} for i, s in enumerate(songs)]
    except:
        pass
    return None

def get_lyric(song_id):
    """获取歌词 + 翻译"""
    url = f"https://music.163.com/api/song/lyric?id={song_id}&lv=1&tv=1"
    try:
        data = fetch(url)
        lrc = data.get("lrc", {}).get("lyric", "") or ""
        trans = data.get("tlyric", {}).get("lyric", "") or ""
        return lrc, trans
    except:
        return "", ""

def parse_lrc_to_text(lrc_text):
    """LRC → 纯文本"""
    lines = []
    for line in lrc_text.split("\n"):
        clean = re.sub(r"\[\d+:\d+\.\d+\]", "", line).strip()
        if clean and not clean.startswith("["):
            lines.append(clean)
    return "\n".join(lines)

def match_track_to_db(track_name, db_tracks):
    """匹配网易云曲目到数据库曲目"""
    tn = norm(track_name)
    for dt in db_tracks:
        if norm(dt["track_name"]) == tn:
            return dt
    # 前缀匹配
    for dt in db_tracks:
        dn = norm(dt["track_name"])
        if tn[:10] and dn[:10] and (tn[:10] in dn[:10] or dn[:10] in tn[:10]):
            return dt
    return None

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    db = sqlite3.connect(DB, timeout=30)
    db.row_factory = sqlite3.Row

    # 查找缺歌词的中文专辑
    albums = db.execute("""
        SELECT a.album_id, a.artist, a.album_name,
               COUNT(lh.id) as listen_cnt,
               SUM(CASE WHEN t.lyrics_text_path IS NOT NULL OR t.lyrics_lrc_path IS NOT NULL THEN 1 ELSE 0 END) as has_cnt,
               COUNT(t.id) as track_cnt
        FROM albums a
        JOIN tracks t ON t.album_id = a.album_id
        LEFT JOIN listen_history lh ON lh.album_id = a.album_id
        WHERE (t.lyrics_text_path IS NULL AND t.lyrics_lrc_path IS NULL)
        GROUP BY a.album_id
        HAVING has_cnt < track_cnt
        ORDER BY listen_cnt DESC, track_cnt DESC
    """).fetchall()

    # 只处理中文专辑（artist 或 album 含中文）
    cn = [a for a in albums if has_chinese(a["artist"]) or has_chinese(a["album_name"])]
    print(f"缺歌词中文专辑: {len(cn)}", flush=True)

    total_ok = 0
    total_fail = 0

    for album in cn[:10]:  # 每轮处理10张
        aid = album["album_id"]
        artist = album["artist"]
        album_name = album["album_name"]
        listen_cnt = album["listen_cnt"]

        print(f"\n{artist} - {album_name} (id={aid}, listens={listen_cnt})", flush=True)

        # 搜索网易云
        wy_id, wy_name = search_album(artist, album_name)
        if not wy_id:
            print(f"  WY: album not found", flush=True)
            total_fail += 1
            continue

        print(f"  WY: {wy_name} (id={wy_id})", flush=True)
        time.sleep(DELAY)

        # 获取曲目
        songs = get_album_songs(wy_id)
        if not songs:
            print(f"  WY: no songs", flush=True)
            total_fail += 1
            continue

        print(f"  WY: {len(songs)} songs", flush=True)
        time.sleep(DELAY)

        # 获取数据库中的曲目
        db_tracks = [dict(r) for r in db.execute(
            "SELECT id, track_number, track_name FROM tracks WHERE album_id = ? AND lyrics_text_path IS NULL AND lyrics_lrc_path IS NULL",
            (aid,)
        ).fetchall()]

        # 创建歌词目录
        save_dir = os.path.join(LYRICS_ROOT, safe_fn(artist), safe_fn(album_name))
        os.makedirs(save_dir, exist_ok=True)

        found = 0
        for song in songs:
            lrc, trans = get_lyric(song["id"], )
            if not lrc:
                time.sleep(DELAY)
                continue

            # 保存文件
            tname = safe_fn(song["name"])
            txt_path = os.path.join(save_dir, f"{tname}.txt")
            lrc_path = os.path.join(save_dir, f"{tname}.lrc")

            # 纯文本
            plain = parse_lrc_to_text(lrc)
            if plain:
                with open(txt_path, "w", encoding="utf-8") as f:
                    f.write(plain)
            # LRC
            with open(lrc_path, "w", encoding="utf-8") as f:
                f.write(lrc)

            # 匹配数据库曲目
            matched = match_track_to_db(song["name"], db_tracks)
            if matched:
                db.execute(
                    "UPDATE tracks SET lyrics_text_path=?, lyrics_lrc_path=? WHERE id=?",
                    (txt_path, lrc_path, matched["id"])
                )
                db_tracks.remove(matched)
                found += 1

            time.sleep(DELAY)

        db.commit()
        print(f"  Matched: {found}/{len(db_tracks) + found}", flush=True)
        total_ok += found

    print(f"\nDone. OK={total_ok} FAIL={total_fail}", flush=True)
    db.close()

if __name__ == "__main__":
    main()
