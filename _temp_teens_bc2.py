import urllib.request, json

# Bandcamp album info via album_id
url = 'https://bandcamp.com/api/album/2/info?album_id=3189506174'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
    print(json.dumps(resp, indent=2)[:2000])
except Exception as e:
    print(f'Error: {e}')
