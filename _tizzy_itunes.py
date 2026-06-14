import urllib.request, json, os

# Try iTunes API for Tizzy Bac
url = 'https://itunes.apple.com/search?term=Tizzy+Bac+%E5%A4%8F%E5%AD%A3%E7%83%AD&media=music&entity=album&limit=5'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
results = resp.get('results', [])
for r in results:
    print(f"Collection: {r.get('collectionName')}")
    print(f"Artist: {r.get('artistName')}")
    print(f"Artwork: {r.get('artworkUrl100')}")
    print(f"URL: {r.get('collectionViewUrl')}")
    print()
