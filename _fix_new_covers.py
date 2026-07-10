import sqlite3, os, urllib.request, ssl

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
COVER_DIR = r'C:\Users\qujt\.qclaw\workspace\album-tracker\public\covers'
ctx = ssl._create_unverified_context()

# 重新下载 iTunes 封面
covers = [
    (604, 'Nando Garcia', 'Lover Man', 'https://is1-ssl.mzstatic.com/image/thumb/Music221/v4/75/63/c3/7563c3bd-0c0a-c8bb-89ad-ecaf8b58d5e3/820200603661.jpg/600x600bb.jpg'),
    (605, 'sueter7', 'Todo Salio Bien', 'https://p1.music.126.net/iEvwlhNSVm7PwdnseTXUVQ==/109951173155579527.jpg'),
]

for aid, artist, album, url in covers:
    fname = f'{aid}-{artist}-{album}.jpg'.replace(' ', '')[:80] + '.jpg'
    # 截断文件名（Windows路径限制）
    safe = ''.join(c for c in fname if c not in r'\\/:*?"<>|')
    fpath = os.path.join(COVER_DIR, safe)
    
    print(f'Downloading {artist} - {album}...')
    print(f'  URL: {url}')
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.126.net/'})
        with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
            data = r.read()
            size = len(data)
            print(f'  Downloaded: {size} bytes ({size/1024:.0f} KB)')
            if size > 10000:
                with open(fpath, 'wb') as f:
                    f.write(data)
                print(f'  Saved: {fpath}')
                # 验证JPEG
                with open(fpath, 'rb') as f:
                    hdr = f.read(4)
                if hdr[:2] == b'\xff\xd8':
                    print(f'  JPEG OK')
                else:
                    print(f'  JPEG FAIL: {hdr}')
            else:
                print(f'  File too small!')
    except Exception as e:
        print(f'  Error: {e}')

print('\nDone')
