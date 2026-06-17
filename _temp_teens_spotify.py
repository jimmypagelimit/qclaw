import urllib.request, json

# Try Spotify API via web
url = 'https://open.spotify.com/oembed?url=https://open.spotify.com/album/0Qvz7b6hPdXo9hGqfFkqHm'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
    print(f"Thumbnail: {resp.get('thumbnail_url')}")
except Exception as e:
    print(f'Error: {e}')
