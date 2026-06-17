import urllib.request, json

url = 'https://api.discogs.com/database/search?q=Car+Seat+Headrest+Teens+of+Style&type=release&per_page=3'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
for r in resp.get('results', []):
    print(f"Title: {r.get('title')} | Thumb: {r.get('thumb')}")
