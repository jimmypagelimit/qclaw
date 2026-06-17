import urllib.request
import urllib.parse
import json
import os

album_name = "Kiss Me Kiss Me Kiss Me"
artist_name = "The Cure"

# Deezer Search API
query = f"{artist_name} {album_name}"
url = f"https://api.deezer.com/search/album?q={urllib.parse.quote(query)}"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
try:
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read())
    if data.get("data"):
        for item in data["data"]:
            print(f"Album: {item.get('title')}")
            print(f"  Artist: {item.get('artist', {}).get('name')}")
            cover = item.get('cover_big', '') or item.get('cover_xl', '')
            print(f"  Cover: {cover}")
            if 'Cure' in item.get('artist', {}).get('name', '') and 'Kiss Me' in item.get('title', ''):
                print(f"  ✓ Matching!")
                if cover:
                    print(f"  Downloading: {cover}")
                    img_req = urllib.request.Request(cover, headers={"User-Agent": "Mozilla/5.0"})
                    img_data = urllib.request.urlopen(img_req, timeout=15).read()
                    print(f"  Size: {len(img_data)} bytes")
                    out_path = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\67-The Cure-Kiss Me Kiss Me Kiss Me.jpg'
                    with open(out_path, 'wb') as f:
                        f.write(img_data)
                    print(f"  Saved: {out_path}")
                    break
    else:
        print("No results from Deezer")
except Exception as e:
    print(f"Error: {e}")
