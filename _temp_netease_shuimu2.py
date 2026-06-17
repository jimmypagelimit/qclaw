import urllib.request
import urllib.parse
import json

query = "水木年华 青春正传"
url = f"https://music.163.com/api/search/get?s={urllib.parse.quote(query)}&type=10&limit=10&offset=0"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://music.163.com/"})
try:
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read().decode('utf-8'))
    if data.get("code") == 200 and data.get("result", {}).get("albums"):
        albums = data["result"]["albums"]
        for i, a in enumerate(albums):
            pic = a['picUrl'].split('?')[0]
            print(f"[{i}] {a['name']} - {a['artist']['name']}")
            print(f"    ID: {a['id']}, Pic: {pic}")
    else:
        print("No results, code:", data.get("code"))
except Exception as e:
    print(f"Error: {e}")
