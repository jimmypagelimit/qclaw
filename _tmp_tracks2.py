import urllib.request, json, sqlite3

# 验证 API 数据结构 + 测试更多专辑
test_albums = [
    (375890593, "悲歌欢唱", "苏紫旭"),
    (381252074, "you seem pretty sad for a girl so in love", "Olivia Rodrigo"),
    (30173981, "Twin Fantasy", "Car Seat Headrest"),
]

headers = {
    "Referer": "https://music.163.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

for aid, aname, aartist in test_albums:
    url = f"https://music.163.com/api/album/{aid}"
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        if data.get("code") != 200:
            print(f"[{aname}] API 失败: {data.get('message','?')}")
            continue
        album = data.get("album", {})
        songs = album.get("songs", [])
        print(f"\n=== {album.get('name','?')} - {album.get('artist',{}).get('name','?')} ===")
        print(f"网易云 ID: {album.get('id')}, 共 {len(songs)} 首")
        for s in songs:
            dur_ms = s.get("duration", 0)
            dur_s = dur_ms // 1000
            # 检查 index 字段到底叫什么
            print(f"  raw: id={s.get('id')}, name={json.dumps(s.get('name',''))}, "
                  f"index_field={s.get('index','N/A')}, "
                  f"albumPosition={s.get('albumPosition','N/A')}, "
                  f"no={s.get('no','N/A')}, "
                  f"cd={s.get('cd','N/A')}, "
                  f"duration={dur_s//60}:{dur_s%60:02d}")
    except Exception as e:
        print(f"[{aname}] 错误: {e}")
