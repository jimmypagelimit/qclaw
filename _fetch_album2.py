import urllib.request, json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://music.163.com/'
}

url = 'https://music.163.com/api/album/35136'
req = urllib.request.Request(url, headers=headers)
resp = urllib.request.urlopen(req, timeout=10)
data = json.loads(resp.read())

# Write full response to file
with open(r'C:\Users\qujt\.qclaw\workspace\_album_response.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print('Keys:', list(data.keys()))
album = data.get('album', {})
print('Album keys:', list(album.keys()) if album else 'None')
print('Code:', data.get('code'))
