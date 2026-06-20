import urllib.request, json, urllib.parse, time, sys

sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://music.163.com'
}

def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    resp = urllib.request.urlopen(req, timeout=10)
    return json.loads(resp.read())

# 搜索刺猬乐队
q = '刺猬乐队 噪音袭击世界'
url = f'https://music.163.com/api/search/get?s={urllib.parse.quote(q)}&type=10&limit=5'
data = fetch(url)
albums = data.get('result', {}).get('albums', [])
print(f'Found {len(albums)} albums')
for a in albums:
    print(f'  id={a["id"]} name={a["name"]}')

if albums:
    al_id = albums[0]['id']
    url2 = f'https://music.163.com/api/album/{al_id}'
    data2 = fetch(url2)
    songs = data2.get('album', {}).get('songs', [])
    print(f'\nAlbum {al_id}: {len(songs)} songs')
    
    if songs:
        # Get lyrics for first 3 songs
        for s in songs[:3]:
            sid = s['id']
            sname = s['name']
            url3 = f'https://music.163.com/api/song/lyric?id={sid}&lv=1&tv=1'
            data3 = fetch(url3)
            lrc = data3.get('lrc', {}).get('lyric', '')
            print(f'  {sname} (id={sid}): lrc_len={len(lrc)}')
            if lrc:
                print(f'    {lrc.split(chr(10))[1][:60]}')
            time.sleep(0.5)
