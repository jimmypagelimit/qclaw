import urllib.request, json, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

tests = [(444, '嘎调'), (425, '灰太阳'), (323, 'Twin Fantasy')]
for album_id, name in tests:
    r = urllib.request.urlopen(f'http://localhost:3456/api/albums/{album_id}').read()
    data = json.loads(r)
    print(f'{name}: keys={list(data.keys())}')
    # 找tracks
    for k, v in data.items():
        if isinstance(v, list) and v:
            print(f'  {k}: {len(v)} items')
            if len(v) > 0:
                item = v[0]
                if isinstance(item, dict):
                    print(f'    first item keys: {list(item.keys())}')
                    lrc = item.get('lyrics_lrc_path')
                    if lrc:
                        print(f'    lyrics_lrc_path: {lrc[-50:]}')
