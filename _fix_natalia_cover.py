import urllib.request, sqlite3, os, ssl, json

COVER_DIR = r'C:\Users\qujt\.qclaw\workspace\album-tracker\public\covers'
DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
ctx = ssl._create_unverified_context()

conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute('SELECT album_id, artist, album_name FROM albums WHERE album_id=458')
r = cur.fetchone()
conn.close()

aid, artist, album = r
print(f'Checking ID={aid}: {artist} - {album}')

# 从iTunes下载
query = 'Natalia Lafourcade Hasta la raiz'
url = 'https://itunes.apple.com/search?term=' + urllib.request.quote(query) + '&entity=album&limit=3'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=10) as resp:
    data = json.loads(resp.read())
    for res in data['results']:
        name = res.get('collectionName', '')
        if 'Hasta' in name or 'raiz' in name.lower():
            cover_url = res['artworkUrl100'].replace('100x100', '600x600')
            print('Found:', name)
            print('Cover URL:', cover_url)
            fname = str(aid) + '-NataliaLafourcade-HastaLaRaiz.jpg'
            fpath = os.path.join(COVER_DIR, fname)
            req2 = urllib.request.Request(cover_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req2, timeout=15, context=ctx) as r2:
                imgdata = r2.read()
                with open(fpath, 'wb') as f:
                    f.write(imgdata)
                print(f'Downloaded: {len(imgdata)} bytes -> {fname}')
            
            # 更新数据库
            db_path = '/covers/' + fname
            conn2 = sqlite3.connect(DB)
            cur2 = conn2.cursor()
            cur2.execute('UPDATE albums SET cover_image_url=? WHERE album_id=?', (db_path, aid))
            conn2.commit()
            conn2.close()
            print('DB updated to:', db_path)
            break
    else:
        print('No matching album found in iTunes results')
