import urllib.request, json, urllib.parse, os
# Search by song name - 王齐铭 生活麻辣烫
url = 'https://music.163.com/api/search/get?s=' + urllib.parse.quote('王齐铭 watchme') + '&type=1&limit=10'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com/'})
data = json.loads(urllib.request.urlopen(req, timeout=10).read())
songs = data.get('result', {}).get('songs', [])
for s in songs:
    album_id = s.get('album', {}).get('id')
    album_name = s.get('album', {}).get('name', '')
    pic_url = s.get('album', {}).get('picUrl', '')
    print(f'album_id={album_id} album={album_name} pic={pic_url}')
