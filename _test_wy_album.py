import urllib.request, json, sys
sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://music.163.com"
}

# 张雨生 口是心非
url = "https://music.163.com/api/album/19026"
req = urllib.request.Request(url, headers=HEADERS)
resp = urllib.request.urlopen(req, timeout=10)
data = json.loads(resp.read())
code = data.get("code")
album = data.get("album", {})
songs = album.get("songs", [])
print(f"code={code}, songs={len(songs)}")

# 如果专辑API不行，用歌曲搜索
url2 = "https://music.163.com/api/search/get?s=%E5%BC%A0%E9%9B%A8%E7%94%9F+%E5%8F%A3%E6%98%AF%E5%BF%83%E9%9D%9E&type=1&limit=30"
req2 = urllib.request.Request(url2, headers=HEADERS)
resp2 = urllib.request.urlopen(req2, timeout=10)
data2 = json.loads(resp2.read())
songs2 = data2.get("result", {}).get("songs", [])
print(f"Song search: {len(songs2)} results")
for s in songs2[:5]:
    al = s.get("album", {})
    print(f"  {s['name']} -> album: {al.get('name','')} (id={al.get('id','')})")
