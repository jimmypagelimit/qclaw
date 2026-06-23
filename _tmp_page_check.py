import urllib.request, json, re

BASE = 'http://127.0.0.1:3456'

# 1. Check homepage HTML
r = urllib.request.urlopen(f'{BASE}/')
html = r.read().decode('utf-8')
print(f"--- Homepage: {r.status}, {(len(html))} bytes ---")

# 2. Check cover URL for album 439
r2 = urllib.request.urlopen(f'{BASE}/api/albums/439')
d = json.loads(r2.read())
print(f"\n--- Album 439: {d.get('album_name')} ---")
print(f"Cover URL: {d.get('cover_image_url')}")

# Verify cover is accessible
cu = d.get('cover_image_url')
if cu:
    r3 = urllib.request.urlopen(f'{BASE}{cu}')
    print(f"Cover accessible: {r3.status}, {len(r3.read())} bytes")

# 3. Check albums 433 and 441 too
for aid in [433, 441]:
    r = urllib.request.urlopen(f'{BASE}/api/albums/{aid}')
    d = json.loads(r.read())
    print(f"\n--- Album {aid}: {d.get('album_name')} ---")
    print(f"Cover URL: {d.get('cover_image_url')}")
    cu = d.get('cover_image_url')
    if cu:
        r3 = urllib.request.urlopen(f'{BASE}{cu}')
        print(f"Cover accessible: {r3.status}, {len(r3.read())} bytes")
