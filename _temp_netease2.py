import urllib.request, os

def download(url, path):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://music.163.com'
    })
    with open(path, 'wb') as f:
        f.write(urllib.request.urlopen(req, timeout=10).read())
    print(f'Downloaded: {path} ({os.path.getsize(path)} bytes)')

# Picture Day - album_id=503
pic_url = 'http://p2.music.126.net/B7QzFwTqvVREl6EcPhTo9g==/109951172872813929.jpg'
download(pic_url, r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\503-The Fencesitters-Picture Day.jpg')

# underscores U - album_id=500
# 先搜索
import urllib.parse, json
url = 'https://music.163.com/api/search/get'
data = urllib.parse.urlencode({'s': 'underscores U album', 'type': 10, 'limit': 5, 'offset': 0}).encode()
req = urllib.request.Request(url, data=data, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com'})
resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
for a in resp.get('result', {}).get('albums', []):
    print(a.get('name'), '|', a.get('artist', {}).get('name'), '|', a.get('picUrl'))
