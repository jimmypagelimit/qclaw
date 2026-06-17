import urllib.request, json, urllib.parse, os
album_name = '生活麻辣烫'
artist_name = '王齐铭'
url = 'https://music.163.com/api/search/get?s=' + urllib.parse.quote(album_name + ' ' + artist_name) + '&type=10&limit=5'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com/'})
data = json.loads(urllib.request.urlopen(req, timeout=10).read())
albums = data.get('result', {}).get('albums', [])
for a in albums:
    aid = a.get('id')
    name = a.get('name')
    artist = a.get('artist', {}).get('name', '')
    pic = a.get('picUrl', '')
    print(f'id={aid}|name={name}|artist={artist}|pic={pic}', flush=True)

# Download first match
if albums:
    a = albums[0]
    pic_url = a.get('picUrl', '')
    if pic_url:
        dest = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\428-王齐铭-生活麻辣烫.jpg'
        req2 = urllib.request.Request(pic_url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com/'})
        resp = urllib.request.urlopen(req2, timeout=10)
        data2 = resp.read()
        with open(dest, 'wb') as f:
            f.write(data2)
        print(f'Downloaded {len(data2)} bytes to {os.path.basename(dest)}', flush=True)
