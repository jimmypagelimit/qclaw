import urllib.request, json

# Deezer
url = 'https://api.deezer.com/search/album?q=Car+Seat+Headrest+Teens+of+Style&limit=5'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
for a in resp.get('data', []):
    print(f"Title: {a.get('title')} | Artist: {a['artist']['name']} | Cover: {a.get('cover_xl')}")
