import urllib.request
import urllib.parse
import json

query = "水木年华 青春正传"
url = f"https://music.163.com/api/search/get?s={urllib.parse.quote(query)}&type=10&limit=10&offset=0"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://music.163.com/"})
try:
    resp = urllib.request.urlopen(req, timeout=10)
    raw = resp.read().decode('utf-8')
    data = json.loads(raw)
    if data.get("code") == 200 and data.get("result", {}).get("albums"):
        albums = data["result"]["albums"]
        for i, a in enumerate(albums):
            name = a['name']
            artist = a['artist']['name']
            pic = a['picUrl'].split('?')[0]
            print(f"[{i}] name={repr(name)}, artist={repr(artist)}")
            print(f"    ID: {a['id']}, Pic: {pic}")
            # Download each cover
            img_req = urllib.request.Request(pic, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://music.163.com/"})
            img_data = urllib.request.urlopen(img_req, timeout=15).read()
            out = rf'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\shuimu_test_{i}.jpg'
            with open(out, 'wb') as f:
                f.write(img_data)
            print(f"    Saved: {out} ({len(img_data)} bytes)")
    else:
        print("No results, code:", data.get("code"))
except Exception as e:
    print(f"Error: {e}")
