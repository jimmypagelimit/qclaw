import urllib.request, json, os, time

headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com/'}

def get(url):
    req = urllib.request.Request(url, headers=headers)
    return json.loads(urllib.request.urlopen(req, timeout=10).read())

targets = [
    (35136, '嘎调', '嘎调'),
    (3070021, '葬尸湖', '冬霾'),
    (263245626, '施鑫文月', '灰太阳'),
]

base = r'C:\Users\qujt\.qclaw\workspace\lyrics'

for album_id, artist, album in targets:
    print(f'处理: {artist} - {album}')
    data = get(f'https://music.163.com/api/album/{album_id}')
    tracks = data.get('album', {}).get('songs', [])
    print(f'  曲目数: {len(tracks)}')
    os.makedirs(f'{base}/{artist}/{album}', exist_ok=True)
    ok = 0
    for t in tracks:
        sid = t['id']
        sname = t['name']
        try:
            ldata = get(f'https://music.163.com/api/song/lyric?id={sid}&lv=-1&kv=-1&tv=-1')
            lrc = ldata.get('lrc', {}).get('lyric', '')
            tlyric = ldata.get('tlyric', {}).get('lyric', '')
            if lrc or tlyric:
                lrc_path = f'{base}/{artist}/{album}/{sname}.lrc'
                with open(lrc_path, 'w', encoding='utf-8') as f:
                    f.write(lrc)
                if tlyric:
                    with open(lrc_path.replace('.lrc', '_zh.lrc'), 'w', encoding='utf-8') as f:
                        f.write(tlyric)
                txt_path = lrc_path.replace('.lrc', '.txt')
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(lrc.replace('\n', '\n'))
                ok += 1
                print(f'  ✅ {sname}')
            else:
                print(f'  ❌ {sname} (no lyric)')
        except Exception as e:
            print(f'  ❌ {sname} (error: {e})')
        time.sleep(0.3)
    print(f'  结果: {ok}/{len(tracks)}')
