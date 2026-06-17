import urllib.request
import urllib.parse
import json
import os

album_name = "Kiss Me Kiss Me Kiss Me"
artist_name = "The Cure"

# Search NetEase API
query = f"{artist_name} {album_name}"
url = f"https://music.163.com/api/search/get?s={urllib.parse.quote(query)}&type=10&limit=5&offset=0"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
try:
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read())
    if data.get("code") == 200 and data.get("result", {}).get("albums"):
        albums = data["result"]["albums"]
        for a in albums:
            print(f"ID: {a['id']}, Name: {a['name']}, Artist: {a['artist']['name']}")
            print(f"  PicUrl: {a['picUrl']}")
            # Check if it matches
            if "Kiss Me" in a['name'] and "Cure" in a['artist']['name']:
                # Download cover
                pic_url = a['picUrl']
                if '?param=' in pic_url:
                    pic_url = pic_url.split('?param=')[0]
                print(f"  Downloading from: {pic_url}")
                img_req = urllib.request.Request(pic_url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://music.163.com/"})
                img_data = urllib.request.urlopen(img_req, timeout=15).read()
                out_path = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\67-The Cure-Kiss Me Kiss Me Kiss Me.jpg'
                with open(out_path, 'wb') as f:
                    f.write(img_data)
                print(f"  Saved: {out_path} ({len(img_data)} bytes)")
                break
    else:
        print("No results or error:", data.get("code"))
except Exception as e:
    print(f"Error: {e}")
