import urllib.request, json

# Bandcamp API
url = 'https://bandcamp.com/api/album/2/info?album_id=3189506174'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
    print(f"ArtID: {resp.get('art_id')}")
except Exception as e:
    print(f'Error: {e}')

# Try the embed endpoint
url2 = 'https://bandcamp.com/EmbeddedPlayer/v=2/album=3189506174/size=large/bgcol=ffffff/linkcol=0687f5/artwork=small'
req2 = urllib.request.Request(url2, headers={'User-Agent': 'Mozilla/5.0'})
try:
    html = urllib.request.urlopen(req2, timeout=10).read().decode()
    # Find image URL
    import re
    m = re.search(r'https://[^"]+\.jpg', html)
    if m:
        print(f'Image: {m.group(0)}')
except Exception as e:
    print(f'Error: {e}')
