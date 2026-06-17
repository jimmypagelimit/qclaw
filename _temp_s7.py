import urllib.request, json, urllib.parse, os

# Search album by artist name 王齐铭
url = 'https://music.163.com/api/search/get?s=' + urllib.parse.quote('王齐铭') + '&type=10&limit=10'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com/'})
data = json.loads(urllib.request.urlopen(req, timeout=10).read())
albums = data.get('result', {}).get('albums', [])
for a in albums:
    aid = a.get('id')
    name = a.get('name')
    artist = a.get('artist', {}).get('name', '')
    pic = a.get('picUrl', '')
    # Save to file for inspection
    with open(r'C:\Users\qujt\.qclaw\workspace\_temp_albums.txt', 'a', encoding='utf-8') as f:
        f.write(f'id={aid}|name={name}|artist={artist}|pic={pic}\n')
print(f"Found {len(albums)} albums")
