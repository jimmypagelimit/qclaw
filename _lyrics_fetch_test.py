import urllib.request, json, sys, io, time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Quick LRCLIB test with a few known tracks
tests = [
    ('Oasis', 'Don\'t Look Back in Anger'),
    ('Daft Punk', 'Veridis Quo'),
    ('Funeral Mist', 'Snakes & Gallows'),
]

start = time.time()
for artist, track in tests:
    url = f'https://lrclib.net/api/search?q={urllib.parse.quote(artist + " " + track)}'
    import urllib.parse
    url = f'https://lrclib.net/api/search?q={urllib.parse.quote(artist + " " + track)}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=5)
        data = json.loads(resp.read())
        status = 'FOUND' if data else 'NONE'
        print(f'{status}: {artist} - {track}')
    except Exception as e:
        print(f'ERR: {artist} - {track}: {e}')

print(f'\nTotal time: {time.time()-start:.1f}s')
