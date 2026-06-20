import urllib.request, json, time

headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com/'}

def get(url):
    req = urllib.request.Request(url, headers=headers)
    return json.loads(urllib.request.urlopen(req, timeout=10).read())

# 测试嘎调 - 嘎调 (id=35136)
album_id = 35136
print(f'正在获取 album id={album_id}...')
data = get(f'https://music.163.com/api/album/{album_id}')
with open(r'C:\Users\qujt\.qclaw\workspace\debug_album.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f'已写入 debug_album.json')
print(f'album 字段存在: {"album" in data}')
print(f'songs 数量: {len(data.get("album", {}).get("songs", []))}')
print(f'code: {data.get("code", "unknown")}')
