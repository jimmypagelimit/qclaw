#!/usr/bin/env python3
"""下载仍然缺失的20张封面"""
import sqlite3, os, json, urllib.request, urllib.parse, time, re

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_music_latest.db')
PUBLIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public', 'covers')
os.makedirs(PUBLIC, exist_ok=True)

HEADERS = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com/'}

conn = sqlite3.connect(DB)
c = conn.cursor()
public_files = set(os.listdir(PUBLIC))

c.execute("SELECT album_id, album_name, artist FROM albums")
missing = []
for row in c.fetchall():
    aid = row[0]
    found = any(f.startswith(f"{aid}-") for f in public_files)
    if not found:
        missing.append(row)

print(f"需下载: {len(missing)} 张")

success = 0
for i, (aid, aname, artist) in enumerate(missing):
    fname = re.sub(r'[\\/:*?"<>|,]', '_', f"{aid}-{artist}-{aname}.jpg")
    path = os.path.join(PUBLIC, fname)
    if os.path.exists(path):
        continue
    
    q = urllib.parse.quote(f"{artist} {aname}")
    img_url = None
    
    # iTunes
    try:
        url = f"https://itunes.apple.com/search?term={q}&entity=album&limit=5"
        data = json.loads(urllib.request.urlopen(url, timeout=10).read())
        if data['resultCount'] > 0:
            for r in data['results']:
                if 'artworkUrl100' in r:
                    big = r['artworkUrl100'].replace('100x100bb', '600x600bb')
                    img_url = big
                    break
    except: pass
    
    # Deezer
    if not img_url:
        try:
            url = f"https://api.deezer.com/search/album?q={q}&limit=5"
            data = json.loads(urllib.request.urlopen(url, timeout=10).read())
            if 'data' in data and len(data['data']) > 0:
                for r in data['data']:
                    if 'cover_big' in r:
                        img_url = r['cover_big']
                        break
        except: pass
    
    # 网易云
    if not img_url:
        try:
            url = f"https://music.163.com/api/search/get/web?csrf_token=&type=10&s={q}&offset=0&limit=5"
            data = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=10).read())
            if data.get('code') == 200:
                for r in data.get('result',{}).get('albums',[]):
                    if 'picUrl' in r:
                        img_url = r['picUrl'].split('?')[0] + '?param=600y600'
                        break
        except: pass
    
    if img_url:
        try:
            req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
            img_data = urllib.request.urlopen(req, timeout=15).read()
            if len(img_data) > 2000:
                with open(path, 'wb') as f:
                    f.write(img_data)
                c.execute("UPDATE albums SET cover_image_url = ? WHERE album_id = ?", (f"/covers/{fname}", aid))
                conn.commit()
                print(f"  ✅ [{i+1}/{len(missing)}] {aid} | {artist} - {aname}")
                success += 1
            else:
                print(f"  ❌ [{i+1}/{len(missing)}] {aid} | {artist} - {aname} (图片太小)")
        except Exception as e:
            print(f"  ❌ [{i+1}/{len(missing)}] {aid} | {artist} - {aname} ({e})")
    else:
        print(f"  ❌ [{i+1}/{len(missing)}] {aid} | {artist} - {aname} (无来源)")
    
    time.sleep(0.5)

print(f"\n完成: {success}/{len(missing)}")
conn.close()