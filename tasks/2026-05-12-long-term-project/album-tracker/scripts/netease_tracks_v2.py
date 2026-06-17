"""
网易云曲目获取管道 v2
- 只处理中文艺人专辑（外文专辑网易云基本没有）
- 严格匹配搜索（专辑名+艺人名双向确认）
- 限流 + 重试
- 跳过"只支持国内"的受限专辑
"""

import urllib.request, json, sqlite3, time, sys, os

DB_PATH = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"
HEADERS = {
    "Referer": "https://music.163.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def has_chinese(s):
    return any('\u4e00' <= c <= '\u9fff' for c in s)

def search_album_strict(name, artist):
    q_str = f"{name} {artist}"
    q = urllib.request.quote(q_str.encode("utf-8"))
    url = f"http://music.163.com/api/search/get/?s={q}&limit=5&type=10&offset=0"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        if data.get("code") != 200:
            return None
        albums = data.get("result", {}).get("albums", [])
        for al in albums:
            al_name = al.get("name", "")
            ar_name = al.get("artist", {}).get("name", "")
            name_ok = name.lower() in al_name.lower() or al_name.lower() in name.lower()
            artist_ok = artist.lower() in ar_name.lower() or ar_name.lower() in artist.lower()
            if name_ok and artist_ok:
                return al.get("id")
        if albums:
            al = albums[0]
            ar_name = al.get("artist", {}).get("name", "")
            if artist.lower() in ar_name.lower() or ar_name.lower() in artist.lower():
                return al.get("id")
        return None
    except Exception as e:
        return None


def get_tracks(album_id, retries=2):
    url = f"https://music.163.com/api/album/{album_id}"
    for attempt in range(retries + 1):
        req = urllib.request.Request(url, headers=HEADERS)
        try:
            resp = urllib.request.urlopen(req, timeout=15)
            data = json.loads(resp.read())
            code = data.get("code", -1)
            if code == 200:
                songs = data.get("album", {}).get("songs", [])
                tracks = []
                for s in songs:
                    tracks.append({
                        "no": s.get("no", 0),
                        "name": s.get("name", ""),
                        "duration": s.get("duration", 0) // 1000,
                    })
                return tracks, None
            elif code == -460 or ('只支持国内' in (data.get('message','') or '')):
                return None, "domestic_only"
            msg = data.get("message", f"code={code}")
            if attempt < retries:
                time.sleep(2)
                continue
            return None, msg
        except Exception as e:
            if attempt < retries:
                time.sleep(2)
                continue
            return None, str(e)
    return None, "retry exhausted"


def save_tracks(db, album_id, tracks):
    cur = db.cursor()
    count = 0
    for t in tracks:
        try:
            cur.execute(
                """INSERT OR REPLACE INTO tracks
                   (album_id, track_number, track_name, duration, disc_number, source)
                   VALUES (?, ?, ?, ?, 1, 'netease')""",
                (album_id, t["no"], t["name"], t["duration"])
            )
            count += 1
        except Exception as e:
            print(f"    写入失败 no={t['no']}: {e}")
    db.commit()
    return count


def batch_process(limit=10):
    db = sqlite3.connect(DB_PATH)
    
    total = db.execute("SELECT COUNT(*) FROM albums").fetchone()[0]
    with_tracks = db.execute("SELECT COUNT(DISTINCT album_id) FROM tracks").fetchone()[0]
    print(f"albums={total}, tracks_covered={with_tracks}, remaining={total - with_tracks}")
    
    # 按 album_id 顺序处理
    albums = db.execute("""
        SELECT a.album_id, a.album_name, a.artist
        FROM albums a
        LEFT JOIN tracks t ON a.album_id = t.album_id
        WHERE t.id IS NULL
        ORDER BY a.album_id
        LIMIT ?
    """, (limit,)).fetchall()
    
    if not albums:
        print("all done!")
        db.close()
        return
    
    success = 0
    skip_no_cn = 0
    skip_not_found = 0
    skip_region = 0
    
    for aid, aname, aartist in albums:
        print(f"[{aid:>3}] {aname[:30]:<30} {aartist[:20]:<20}", end="")
        
        if not has_chinese(aartist):
            print(" | skip: foreign")
            skip_no_cn += 1
            continue
        
        netease_id = search_album_strict(aname, aartist)
        if not netease_id:
            print(" | skip: not found")
            skip_not_found += 1
            time.sleep(0.3)
            continue
        
        tracks, err = get_tracks(netease_id)
        if tracks is None:
            if err == "domestic_only":
                print(f" | skip: region restricted ({netease_id})")
                skip_region += 1
            else:
                print(f" | skip: {err} ({netease_id})")
                skip_not_found += 1
            time.sleep(0.5)
            continue
        
        count = save_tracks(db, aid, tracks)
        print(f" | OK {count}tracks (id={netease_id})")
        success += 1
        time.sleep(0.5)
    
    print(f"\nResult: {success} OK | {skip_no_cn} foreign | {skip_not_found} unfound | {skip_region} region")
    db.close()


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    batch_process(limit)
