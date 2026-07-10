#!/usr/bin/env python3
"""下载Madonna Confessions II封面"""
import sqlite3, os, urllib.request, json

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
COVER_DIR = r'C:\Users\qujt\.qclaw\workspace\album-tracker\public\covers'

# iTunes搜索
query = urllib.request.quote('Madonna Confessions II')
url = f'https://itunes.apple.com/search?term={query}&entity=album&limit=3'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=10) as r:
    data = json.loads(r.read())
    print(f'Results: {data.get("resultCount")}')
    for res in data['results']:
        name = res.get('collectionName', '')
        print(f'  - {name}')
        if 'Confessions' in name:
            artwork = res.get('artworkUrl100', '').replace('100x100', '600x600')
            print(f'  Cover URL: {artwork}')
            cover_path = os.path.join(COVER_DIR, 'Madonna-Confessions-II.jpg')
            try:
                req2 = urllib.request.Request(artwork, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req2, timeout=10) as r2:
                    img_data = r2.read()
                    if len(img_data) > 5000:
                        with open(cover_path, 'wb') as f:
                            f.write(img_data)
                        print(f'  Saved: {len(img_data)} bytes')
                        # 更新数据库
                        conn = sqlite3.connect(DB)
                        cur = conn.cursor()
                        cur.execute("UPDATE albums SET cover_image_url='/covers/Madonna-Confessions-II.jpg' WHERE album_id=603")
                        conn.commit()
                        conn.close()
                        print('  DB updated')
                    else:
                        print('  File too small')
            except Exception as e:
                print(f'  Error: {e}')
            break
