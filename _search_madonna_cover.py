#!/usr/bin/env python3
import urllib.request, json

query = urllib.request.quote('Confessions II 2026 Madonna')
url = f'https://itunes.apple.com/search?term={query}&entity=album&limit=5'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=10) as r:
    data = json.loads(r.read())
    count = data.get('resultCount')
    print(f'Results: {count}')
    for res in data['results']:
        name = res.get('collectionName', '')
        year = res.get('releaseDate', '')[:4]
        artist = res.get('artistName', '')
        artwork = res.get('artworkUrl100', '').replace('100x100', '600x600')
        print(f'  [{year}] {artist} - {name}')
        print(f'  Cover: {artwork}')
        print()
