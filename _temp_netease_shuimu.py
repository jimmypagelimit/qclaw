import urllib.request
import urllib.parse
import json
import os

album_name = "青春正传"
artist_name = "水木年华"

# Search NetEase API
query = f"{artist_name} {album_name}"
url = f"https://music.163.com/api/search/get?s={urllib.parse.quote(query)}&type=10&limit=5&offset=0"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://music.163.com/"})
try:
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read().decode('utf-8'))
    if data.get("code") == 200 and data.get("result", {}).get("albums"):
        for a in data["result"]["albums"]:
            aname = a['name']
            art = a['artist']['name']
            print(f"Found: {aname} - {art}")
            if "青春" in aname and "水木" in art:
                pic_url = a['picUrl'].split('?')[0]
                print(f"  Downloading from: {pic_url}")
                img_req = urllib.request.Request(pic_url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://music.163.com/"})
                img_data = urllib.request.urlopen(img_req, timeout=15).read()
                out_path = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\123-水木年华-青春正传.jpg'
                with open(out_path, 'wb') as f:
                    f.write(img_data)
                print(f"  Saved: {out_path} ({len(img_data)} bytes)")
                # Update DB
                import sqlite3
                db = 'C:/Users/qujt/.qclaw/workspace/_music_latest.db'
                conn = sqlite3.connect(db)
                c = conn.cursor()
                c.execute("UPDATE albums SET cover_image_url='/covers/123-水木年华-青春正传.jpg' WHERE album_id=123")
                conn.commit()
                print(f"  DB updated: cover_image_url set")
                conn.close()
                break
    else:
        print("No results, code:", data.get("code"))
except Exception as e:
    print(f"Error: {e}")
