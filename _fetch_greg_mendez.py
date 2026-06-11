import urllib.request, json, urllib.parse

# Apple Music details - get the actual collectionId first
req = urllib.request.Request('https://itunes.apple.com/search?term=Greg+Mendez+Beauty+Land&entity=album&limit=5', headers={'User-Agent': 'iTunes/12.0'})
data = json.loads(urllib.request.urlopen(req, timeout=10).read())
print('=== Apple Music Search ===')
for r in data.get('results', []):
    print('ID:', r.get('collectionId'))
    print('Name:', r.get('collectionName'))
    print('Artist:', r.get('artistName'))
    print('Release:', r.get('releaseDate'))
    print('Genre:', r.get('primaryGenreName'))
    print('Tracks:', r.get('trackCount'))
    print('Artwork:', r.get('artworkUrl100', '').replace('100x100bb', '3000x3000bb'))
    print()

# Apple Music tracks lookup
for r in data.get('results', []):
    cid = r.get('collectionId')
    if not cid:
        continue
    req2 = urllib.request.Request(f'https://itunes.apple.com/lookup?id={cid}&entity=song', headers={'User-Agent': 'iTunes/12.0'})
    data2 = json.loads(urllib.request.urlopen(req2, timeout=10).read())
    print(f'=== Tracks for {r.get("collectionName")} ===')
    for t in data2.get('results', []):
        if t.get('wrapperType') == 'track':
            tn = t.get('trackNumber', '?')
            name = t.get('trackName', '?')
            ms = t.get('trackTimeMillis', 0)
            mins = ms // 60000
            secs = (ms % 60000) // 1000
            print(f'  {tn}. {name} ({mins}:{secs:02d})')
    print()

# Discogs details for id 37489077
req3 = urllib.request.Request('https://api.discogs.com/releases/37489077', headers={'User-Agent': 'OpenClaw/1.0'})
data3 = json.loads(urllib.request.urlopen(req3, timeout=15).read())
print('=== Discogs ===')
print('Title:', data3.get('title'))
for a in data3.get('artists', []):
    print('Artist:', a.get('name'), a.get('join', ''))
print('Year:', data3.get('year'))
print('Genres:', data3.get('genres', []))
print('Styles:', data3.get('styles', []))
print('Format:', [(f.get('name'), f.get('qty'), f.get('descriptions')) for f in data3.get('formats', [])])
print('Tracks:')
for t in data3.get('tracklist', []):
    print(f'  {t.get("position","")}. {t.get("title","")} ({t.get("duration","")})')
