import urllib.request, json, os, time

headers = {
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://music.163.com/'
}

def get_album_tracks(album_id):
    url = f'https://music.163.com/api/album/{album_id}'
    req = urllib.request.Request(url, headers=headers)
    data = json.loads(urllib.request.urlopen(req, timeout=10).read())
    return data.get('album', {}).get('songs', [])

def get_lyrics(song_id):
    url = f'https://music.163.com/api/song/lyric?id={song_id}&lv=-1&kv=-1&tv=-1'
    req = urllib.request.Request(url, headers=headers)
    try:
        data = json.loads(urllib.request.urlopen(req, timeout=10).read())
        lrc = data.get('lrc', {}).get('lyric', '')
        tlyric = data.get('tlyric', {}).get('lyric', '')
        return lrc, tlyric
    except:
        return '', ''

# 已知 album id（从搜索结果得到）
targets = [
    (35136, '嘎调', '嘎调'),
    (370393422, '東京酒吐座', 'Remains'),
    (3070021, '葬尸湖', '冬霾'),
    (263245626, '施鑫文月', '灰太阳'),
]

base = r'C:\Users\qujt\.qclaw\workspace\lyrics'

for album_id, artist, album in targets:
    print(f'\n处理: {artist} - {album} (album_id={album_id})')
    tracks = get_album_tracks(album_id)
    print(f'  曲目数: {len(tracks)}')
    os.makedirs(f'{base}/{artist}/{album}', exist_ok=True)
    ok = 0
    for t in tracks:
        sid = t['id']
        sname = t['name']
        lrc, tlyric = get_lyrics(sid)
        if lrc or tlyric:
            path = f'{base}/{artist}/{album}/{sname}.lrc'
            with open(path, 'w', encoding='utf-8') as f:
                f.write(lrc)
            if tlyric:
                with open(path.replace('.lrc', '_zh.lrc'), 'w', encoding='utf-8') as f:
                    f.write(tlyric)
            print(f'  ✅ {sname}')
            ok += 1
        else:
            print(f'  ❌ {sname} (no lyric)')
        time.sleep(0.3)
    print(f'  结果: {ok}/{len(tracks)}')
