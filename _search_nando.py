#!/usr/bin/env python3
import urllib.request, json

query = urllib.request.quote('Nando Garcia Lover Man')
url = f'https://itunes.apple.com/search?term={query}&entity=album&limit=10'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=10) as r:
    data = json.loads(r.read())
    count = data.get('resultCount')
    print(f'iTunes Results: {count}')
    for res in data['results']:
        name = res.get('collectionName', '')
        artist = res.get('artistName', '')
        year = res.get('releaseDate', '')[:4]
        artwork = res.get('artworkUrl100', '').replace('100x100', '600x600')
        genre = res.get('primaryGenreName', '')
        print(f'  [{year}] {artist} - {name} ({genre})')
        print(f'  Cover: {artwork}')
        print()
