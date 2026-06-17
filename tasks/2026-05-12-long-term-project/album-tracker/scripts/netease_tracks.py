"""
网易云曲目获取管道
1. 从 albums 表查出没有曲目的专辑
2. 搜索网易云（专辑名 + 艺人）
3. 获取曲目列表
4. 写入 tracks 表
"""

import urllib.request, json, sqlite3, time, re, sys

DB_PATH = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"
HEADERS = {
    "Referer": "https://music.163.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def search_album(name, artist):
    """搜索网易云专辑"""
    q = urllib.request.quote(f"{name} {artist}".encode("utf-8"))
    url = f"http://music.163.com/api/search/get/?s={q}&limit=5&type=10&offset=0"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        if data.get("code") != 200:
            return None
        results = data.get("result", {}).get("albums", [])
        for album in results:
            al_name = album.get("name", "")
            ar_name = album.get("artist", {}).get("name", "")
            # 宽松匹配：专辑名和艺人名包含关键词
            if (name.lower() in al_name.lower() or al_name.lower() in name.lower()) and \
               (artist.lower() in ar_name.lower() or ar_name.lower() in artist.lower()):
                return album.get("id")
        # 如果精确匹配不到，返回第一个结果
        return results[0].get("id") if results else None
    except Exception as e:
        print(f"  搜索失败: {e}")
        return None


def get_tracks(album_id):
    """获取专辑曲目列表"""
    url = f"https://music.163.com/api/album/{album_id}"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        if data.get("code") != 200:
            return None, data.get("message", "")
        album = data.get("album", {})
        songs = album.get("songs", [])
        tracks = []
        for s in songs:
            tracks.append({
                "no": s.get("no", 0),
                "name": s.get("name", ""),
                "duration": s.get("duration", 0) // 1000,  # ms -> seconds
                "netease_song_id": s.get("id"),
            })
        return tracks, None
    except Exception as e:
        return None, str(e)


def save_tracks(db, album_id, tracks, source="netease"):
    """写入 tracks 表"""
    cur = db.cursor()
    count = 0
    for t in tracks:
        try:
            cur.execute(
                """INSERT OR REPLACE INTO tracks 
                   (album_id, track_number, track_name, duration, disc_number, source)
                   VALUES (?, ?, ?, ?, 1, ?)""",
                (album_id, t["no"], t["name"], t["duration"], source)
            )
            count += 1
        except Exception as e:
            print(f"  写入失败 no={t['no']}: {e}")
    db.commit()
    return count


def get_albums_without_tracks(db, limit=10):
    """查出没有曲目的专辑"""
    rows = db.execute("""
        SELECT a.album_id, a.album_name, a.artist
        FROM albums a
        LEFT JOIN tracks t ON a.album_id = t.album_id
        WHERE t.id IS NULL
        ORDER BY a.album_id
        LIMIT ?
    """, (limit,)).fetchall()
    return rows


if __name__ == "__main__":
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    
    db = sqlite3.connect(DB_PATH)
    
    # 先统计
    total = db.execute("SELECT COUNT(*) FROM albums").fetchone()[0]
    with_tracks = db.execute("SELECT COUNT(DISTINCT album_id) FROM tracks").fetchone()[0]
    print(f"专辑总数: {total}, 已有曲目: {with_tracks}, 待处理: {total - with_tracks}")
    print()
    
    albums = get_albums_without_tracks(db, limit)
    
    if not albums:
        print("所有专辑已有曲目！")
        db.close()
        sys.exit(0)
    
    success = 0
    fail = 0
    
    for aid, aname, aartist in albums:
        print(f"[{aid}] {aname} - {aartist}")
        
        netease_id = search_album(aname, aartist)
        if not netease_id:
            print(f"  -> 网易云未找到")
            fail += 1
            continue
        
        print(f"  -> 网易云 ID: {netease_id}")
        
        tracks, err = get_tracks(netease_id)
        if tracks is None:
            print(f"  -> 获取曲目失败: {err}")
            fail += 1
            time.sleep(1)
            continue
        
        count = save_tracks(db, aid, tracks)
        print(f"  -> 写入 {count} 首曲目")
        success += 1
        
        # 接口限流
        time.sleep(0.5)
    
    print(f"\n完成: 成功 {success}/{len(albums)}, 失败 {fail}")
    db.close()
