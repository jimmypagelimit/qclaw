import urllib.request, json, urllib.parse, time, sys, os

sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://music.163.com'
}

def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    resp = urllib.request.urlopen(req, timeout=10)
    return json.loads(resp.read())

# 张悬 My Life Will
url = 'https://music.163.com/api/album/32315'
data = fetch(url)
songs = data.get('album', {}).get('songs', [])
print(f'Album: {len(songs)} songs')

for s in songs[:5]:
    sid = s['id']
    sname = s['name']
    # Get lyrics
    url2 = f'https://music.163.com/api/song/lyric?id={sid}&lv=1&tv=1'
    data2 = fetch(url2)
    lrc = data2.get('lrc', {}).get('lyric', '')
    trans = data2.get('tlyric', {}).get('lyric', '')
    print(f'  {sname} (id={sid}): lrc={len(lrc)} trans={len(trans)}')
    if lrc:
        lines = lrc.split('\n')
        for l in lines[:3]:
            if l.strip():
                print(f'    {l.strip()[:60]}')
    time.sleep(0.5)
