import urllib.request, json, sqlite3

# 试试网易云 API
album_id_netease = 375890593
url = f"https://music.163.com/api/album/{album_id_netease}"
headers = {
    "Referer": "https://music.163.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
req = urllib.request.Request(url, headers=headers)
try:
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read())
    code = data.get("code", -1)
    print(f"API 返回 code: {code}")
    if code == 200:
        album = data.get("album", {})
        print(f"专辑: {album.get('name','?')}")
        print(f"艺人: {album.get('artist',{}).get('name','?')}")
        songs = album.get("songs", [])
        print(f"歌曲数: {len(songs)}")
        for s in songs:
            dur_ms = s.get("duration", 0)
            dur_s = dur_ms // 1000
            idx = s.get("index", "?")
            name = s.get("name", "?")
            print(f"  {idx:>2}. {name}  {dur_s//60}:{dur_s%60:02d}")
    else:
        print(f"API 错误: {data.get('message','未知')}")
        print("需要登录态，试试浏览器方案...")
except Exception as e:
    print(f"API 失败: {e}")

# 尝试用 urllib.request 自动携带 cookie（可能能复用浏览器 cookie）
# 但 urllib 不共享浏览器 cookie，所以走不通
print("\n建议走 opencli 浏览器方案")
