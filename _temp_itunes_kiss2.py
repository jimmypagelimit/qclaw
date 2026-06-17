import urllib.request
import urllib.parse
import json
import os

album_name = "Kiss Me Kiss Me Kiss Me"
artist_name = "The Cure"

# iTunes Search API
query = f"{artist_name} {album_name}"
url = f"https://itunes.apple.com/search?term={urllib.parse.quote(query)}&entity=album&limit=10"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
try:
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read())
    found = False
    for item in data.get("results", []):
        coll = item.get('collectionName', '')
        artist = item.get('artistName', '')
        print(f"Collection: {coll}")
        print(f"  Artist: {artist}")
        # Filter for The Cure + Kiss Me Kiss Me Kiss Me
        if 'Cure' in artist and 'Kiss Me' in coll:
            print(f"  ✓ Matching!")
            art_url = item.get('artworkUrl100', '').replace('100x100bb', '600x600bb')
            if art_url:
                print(f"  Downloading: {art_url}")
                img_req = urllib.request.Request(art_url, headers={"User-Agent": "Mozilla/5.0"})
                img_data = urllib.request.urlopen(img_req, timeout=15).read()
                print(f"  Size: {len(img_data)} bytes")
                out_path = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\67-The Cure-Kiss Me Kiss Me Kiss Me.jpg'
                with open(out_path, 'wb') as f:
                    f.write(img_data)
                print(f"  Saved: {out_path}")
                found = True
                break
    if not found:
        print("The Cure album not found in iTunes results")
except Exception as e:
    print(f"Error: {e}")
