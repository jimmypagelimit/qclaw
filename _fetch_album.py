import urllib.request, json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://music.163.com/'
}

def fetch_album(album_id):
    url = f'https://music.163.com/api/album/{album_id}'
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=10)
    return json.loads(resp.read())

# Test with album 35136 (嘎调)
result = fetch_album(35136)
songs = result.get('album', {}).get('songs', [])
print(f'Got {len(songs)} songs from album 35136')
for s in songs:
    print(f'  {s["id"]}: {s["name"]}')
