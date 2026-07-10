import sqlite3, os

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
COVER_DIR = r'C:\Users\qujt\.qclaw\workspace\album-tracker\public\covers'

conn = sqlite3.connect(DB)
cur = conn.cursor()

# 检查最近入库的封面
recent_ids = [603, 604, 605, 458]
for aid in recent_ids:
    cur.execute("SELECT album_id, artist, album_name, cover_image_url FROM albums WHERE album_id=?", (aid,))
    row = cur.fetchone()
    if row:
        aid2, artist, album, curl = row
        print(f'\nID={aid2}: {artist} - {album}')
        print(f'  DB path: {curl}')
        if curl:
            fname = curl.replace('/covers/', '')
            fpath = os.path.join(COVER_DIR, fname)
            print(f'  File path: {fpath}')
            if os.path.exists(fpath):
                size = os.path.getsize(fpath)
                print(f'  Size: {size} bytes ({size/1024:.0f} KB)')
                # 检查JPEG头
                with open(fpath, 'rb') as f:
                    header = f.read(20)
                if header[:2] == b'\xff\xd8':
                    print(f'  JPEG header: OK')
                else:
                    print(f'  JPEG header: FAIL - {header[:4]}')
            else:
                print(f'  File NOT FOUND!')
        else:
            print(f'  No cover in DB!')
conn.close()
