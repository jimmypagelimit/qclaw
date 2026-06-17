import urllib.request, json, urllib.parse, os, sqlite3

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
COVERS = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers'
HEADERS = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com/'}

# Search for The Cure self-titled album
url = 'https://music.163.com/api/search/get?s=The+Cure+The+Cure&type=10&limit=10'
req = urllib.request.Request(url, headers=HEADERS)
data = json.loads(urllib.request.urlopen(req, timeout=10).read())
albums = data.get('result', {}).get('albums', [])
for a in albums:
    print(f'id={a.get("id")} name={a.get("name")} artist={a.get("artist",{}).get("name","")} pic={a.get("picUrl","")}')
    with open(r'C:\Users\qujt\.qclaw\workspace\_temp_cure_list.txt', 'a', encoding='utf-8') as f:
        f.write(f'id={a.get("id")} name={a.get("name")} artist={a.get("artist",{}).get("name","")} pic={a.get("picUrl","")}\n')
