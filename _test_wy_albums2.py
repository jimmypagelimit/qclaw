import urllib.request, json, sys, time
sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://music.163.com"
}

def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    resp = urllib.request.urlopen(req, timeout=15)
    return json.loads(resp.read())

# 测试几张专辑
test_ids = [
    (19026, "张雨生 口是心非"),
    (29725, "王菲 唱游"),
    (37805, "Tizzy Bac 如果看见地狱"),
    (19242, "郑智化 堕落天使"),
    (35954, "葬尸湖 奕秋"),
]

for al_id, name in test_ids:
    url = f"https://music.163.com/api/album/{al_id}"
    data = fetch(url)
    songs = data.get("album", {}).get("songs", [])
    print(f"{name} (id={al_id}): {len(songs)} songs")
    if songs:
        # 获取第一首歌词
        sid = songs[0]["id"]
        url2 = f"https://music.163.com/api/song/lyric?id={sid}&lv=1&tv=1"
        data2 = fetch(url2)
        lrc = data2.get("lrc", {}).get("lyric", "")
        print(f"  First song id={sid}, lrc_len={len(lrc)}")
    time.sleep(0.8)
