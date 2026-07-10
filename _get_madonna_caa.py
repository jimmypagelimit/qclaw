#!/usr/bin/env python3
"""下载Madonna Confessions II封面 - Cover Art Archive"""
import sqlite3, os, urllib.request, ssl

COVER_DIR = r'C:\Users\qujt\.qclaw\workspace\album-tracker\public\covers'
DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'

# Worldwide digital release ID
release_id = '5090e9e3-fc35-4f57-b87f-b40f4392e5af'
cover_url = f'https://coverartarchive.org/release/{release_id}/front-500'

print(f'Downloading from: {cover_url}')

cover_path = os.path.join(COVER_DIR, 'Madonna-Confessions-II.jpg')

ctx = ssl._create_unverified_context()
try:
    req = urllib.request.Request(cover_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
        data = r.read()
        print(f'Response size: {len(data)} bytes')
        if len(data) > 5000:
            with open(cover_path, 'wb') as f:
                f.write(data)
            print(f'Saved to: {cover_path}')
            
            # Update DB
            conn = sqlite3.connect(DB)
            cur = conn.cursor()
            cur.execute("UPDATE albums SET cover_image_url='/covers/Madonna-Confessions-II.jpg' WHERE album_id=603")
            conn.commit()
            conn.close()
            print('DB updated')
        else:
            print('File too small')
except Exception as e:
    print(f'Error: {e}')
