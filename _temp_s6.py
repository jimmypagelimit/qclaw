import urllib.request, json, os

# Try album detail directly for the potential match
for album_id in [289139414, 289139414]:
    url = f'https://music.163.com/api/album/{album_id}'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com/'})
    try:
        data = json.loads(urllib.request.urlopen(req, timeout=10).read())
        album = data.get('album', {})
        name = album.get('name', '')
        artist = album.get('artist', {}).get('name', '')
        pic = album.get('picUrl', '')
        print(f'album_id={album_id} name={name} artist={artist} pic={pic}', flush=True)
        if pic and '生活麻辣烫' in name:
            dest = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\428-王齐铭-生活麻辣烫.jpg'
            req2 = urllib.request.Request(pic, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com/'})
            resp = urllib.request.urlopen(req2, timeout=10)
            data2 = resp.read()
            with open(dest, 'wb') as f:
                f.write(data2)
            print(f'Downloaded {len(data2)} bytes', flush=True)
            break
    except Exception as e:
        print(f'Error for {album_id}: {e}')
