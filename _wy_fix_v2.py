import urllib.request, json, os, time, sqlite3

headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com/'}

def get(url):
    req = urllib.request.Request(url, headers=headers)
    return json.loads(urllib.request.urlopen(req, timeout=10).read())

# 已知网易云 album id
targets = [
    (35136, '嘎调', '嘎调'),
    (370393422, '東京酒吐座', 'Remains'),
    (3070021, '葬尸湖', '冬霾'),
    (263245626, '施鑫文月', '灰太阳'),
]

base = r'C:\Users\qujt\.qclaw\workspace\lyrics'
db_path = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'

conn = sqlite3.connect(db_path)
conn.execute('PRAGMA journal_mode=WAL')

for album_id, artist, album in targets:
    print(f'\n处理: {artist} - {album} (wy_album_id={album_id})')
    try:
        data = get(f'https://music.163.com/api/album/{album_id}')
        tracks = data.get('album', {}).get('songs', [])
        print(f'  网易云曲目数: {len(tracks)}')
        os.makedirs(f'{base}/{artist}/{album}', exist_ok=True)
        ok = 0
        for t in tracks:
            sid = t['id']
            sname = t['name']
            # 获取歌词
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
                    # 写入 txt
                    txt_path = lrc_path.replace('.lrc', '.txt')
                    with open(txt_path, 'w', encoding='utf-8') as f:
                        f.write(lrc.replace('\n', '\n'))
                    ok += 1
            except Exception as e:
                pass
            time.sleep(0.3)
        print(f'  获取歌词: {ok}/{len(tracks)}')
    except Exception as e:
        print(f'  错误: {e}')

conn.close()
print('\nDone')
