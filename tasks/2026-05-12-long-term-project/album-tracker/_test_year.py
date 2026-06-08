import urllib.request, json

url = 'http://127.0.0.1:3456/api/albums?year=2026&offset=0&limit=5'
data = json.loads(urllib.request.urlopen(url, timeout=5).read())
print(f'Total: {data.get("total")}')
for a in data.get('albums', []):
    name = a.get('album_name', '')
    artist = a.get('artist', '')
    yl = a.get('year_listen_count', 0)
    print(f'  {name} - {artist} ({yl} listens)')
