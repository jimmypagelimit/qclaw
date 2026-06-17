import urllib.request, urllib.parse, json

# iTunes Search API
url = 'https://itunes.apple.com/search?term=%E6%96%BD%E9%91%AB%E6%96%87%E6%9C%88+%E5%B7%B4%E8%9C%80%E6%96%87%E8%89%BA%E5%A4%8D%E5%85%B4+%E7%AC%AC%E4%B8%80%E7%AB%A0&entity=album&limit=5'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
for r in resp.get('results', []):
    print(f"Name: {r.get('collectionName')} | Artist: {r.get('artistName')} | Artwork: {r.get('artworkUrl100').replace('100x100', '600x600')}")
