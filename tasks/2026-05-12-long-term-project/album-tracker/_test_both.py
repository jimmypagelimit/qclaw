import urllib.request, json

# Test 2026 listen_year
url = 'http://127.0.0.1:3456/api/albums?year=2026&offset=0&limit=200'
data = json.loads(urllib.request.urlopen(url, timeout=5).read())
total = data.get('total', 0)
print(f'2026 listen_year total: {total}')

# Find Hiperson
for a in data.get('albums', []):
    artist = a.get('artist', '')
    if 'Hiperson' in artist or 'hiperson' in artist.lower():
        print(f"  FOUND: {a.get('album_name')} - {artist} (yl:{a.get('year_listen_count')})")

# Find Paul
for a in data.get('albums', []):
    artist = a.get('artist', '')
    if 'Paul McCartney' in artist:
        print(f"  FOUND: {a.get('album_name')} - {artist} (yl:{a.get('year_listen_count')})")
