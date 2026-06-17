import urllib.request, json, sqlite3, time

DB_PATH = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"
HEADERS = {
    "Referer": "https://music.163.com/",
    "User-Agent": "Mozilla/5.0"
}

db = sqlite3.connect(DB_PATH)

# 看看前20张无曲目的专辑
albums = db.execute("""
    SELECT a.album_id, a.album_name, a.artist
    FROM albums a
    LEFT JOIN tracks t ON a.album_id = t.album_id
    WHERE t.id IS NULL
    ORDER BY a.album_id
    LIMIT 20
""").fetchall()

for aid, aname, aartist in albums:
    # 判断是否是中文艺人
    has_chinese = any('\u4e00' <= c <= '\u9fff' for c in aartist)
    print(f"[{aid:>3}] {aname[:30]:<30} {aartist[:20]:<20} {'中文' if has_chinese else '外文'}")
    if not has_chinese:
        continue  # 外文基本搜不到
    
    # 搜索中文专
    q_str = f"{aname} {aartist}"
    q = urllib.request.quote(q_str.encode("utf-8"))
    url = f"http://music.163.com/api/search/get/?s={q}&limit=3&type=10&offset=0"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        albums_list = data.get("result", {}).get("albums", [])
        if albums_list:
            al = albums_list[0]
            netease_id = al.get("id", "?")
            al_name = al.get("name", "")
            ar_name = al.get("artist", {}).get("name", "")
            print(f"  搜到: [{netease_id}] {al_name} - {ar_name}")
            # 验证匹配度
            match = (aname.lower() in al_name.lower()) and (aartist.lower() in ar_name.lower())
            print(f"  精确匹配: {'✅' if match else '❌'}")
        else:
            print(f"  搜不到")
    except Exception as e:
        print(f"  搜索失败: {e}")
    time.sleep(0.3)

db.close()
