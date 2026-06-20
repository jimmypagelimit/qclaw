import urllib.request, json, time

headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com/'}

# 从之前搜索结果里拿到 album id
check_ids = [35136, 370393422, 3070021, 263245626, 174880171, 381124020]

for aid in check_ids:
    url = f'https://music.163.com/api/album/{aid}'
    req = urllib.request.Request(url, headers=headers)
    try:
        data = json.loads(urllib.request.urlopen(req, timeout=10).read())
        code = data.get('code', 'unknown')
        album = data.get('album', {})
        name = album.get('name', 'unknown')
        songs_count = len(album.get('songs', []))
        print(f'id={aid}: code={code}, name={name}, songs={songs_count}')
    except Exception as e:
        print(f'id={aid}: ERROR {e}')
    time.sleep(0.5)
