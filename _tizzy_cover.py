import urllib.request, os

# Try different NetEase cover URL formats
pic_id = '109951172445569812'
album_id = 37819

urls = [
    f'http://p3.music.126.net/{pic_id}/{album_id}.jpg',
    f'http://p1.music.126.net/{pic_id}/{album_id}.jpg',
    f'http://p2.music.126.net/{pic_id}/{album_id}.jpg',
    f'https://p3.music.126.net/{pic_id}/{album_id}.jpg',
    f'http://music.126.net/{pic_id}/{album_id}.jpg',
]

cover_path = r'C:\Users\qujt\.qclaw\workspace\album-tracker\public\covers\558-Tizzy_Bac-夏季热.jpg'

for url in urls:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'http://music.163.com/'})
        resp = urllib.request.urlopen(req, timeout=5)
        data = resp.read()
        with open(cover_path, 'wb') as f:
            f.write(data)
        print(f"Success: {url} ({len(data)} bytes)")
        break
    except Exception as e:
        print(f"Failed: {url} -> {e}")
