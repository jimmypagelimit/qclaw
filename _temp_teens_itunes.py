import urllib.request, json

# iTunes
url = 'https://itunes.apple.com/search?term=Car+Seat+Headrest+Teens+of+Style&entity=album&limit=5'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
for r in resp.get('results', []):
    print(f"Name: {r.get('collectionName')} | Artwork: {r.get('artworkUrl100').replace('100x100', '1200x1200')}")
