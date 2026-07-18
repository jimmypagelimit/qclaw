#!/usr/bin/env python3
"""下载缺失专辑封面"""
import sqlite3, os, json, urllib.request, urllib.parse, urllib.error, time, re, sys

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_music_latest.db')
PUBLIC_COVERS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public', 'covers')
os.makedirs(PUBLIC_COVERS, exist_ok=True)

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}

def sanitize(s):
    """文件名安全"""
    return re.sub(r'[\\/:*?"<>|,]', '_', str(s).strip())

def safe_filename(aid, artist, album):
    return f"{aid}-{sanitize(artist)}-{sanitize(album)}.jpg"

def urlopen(url, timeout=10):
    req = urllib.request.Request(url, headers=HEADERS)
    return urllib.request.urlopen(req, timeout=timeout)

# ---- Sources ----

def itunes_search(artist, album):
    """iTunes Search API"""
    q = urllib.parse.quote(f"{artist} {album}")
    url = f"https://itunes.apple.com/search?term={q}&entity=album&limit=5"
    try:
        data = json.loads(urlopen(url).read())
        if data['resultCount'] > 0:
            for r in data['results']:
                if 'artworkUrl100' in r:
                    # 100x100 -> 600x600
                    big = r['artworkUrl100'].replace('100x100bb', '600x600bb')
                    return big
    except Exception as e:
        pass
    return None

def deezer_search(artist, album):
    """Deezer API"""
    q = urllib.parse.quote(f"{artist} {album}")
    url = f"https://api.deezer.com/search/album?q={q}&limit=5"
    try:
        data = json.loads(urlopen(url).read())
        if 'data' in data and len(data['data']) > 0:
            for r in data['data']:
                if 'cover_big' in r:
                    return r['cover_big']
                if 'cover_medium' in r:
                    return r['cover_medium']
                if 'cover' in r:
                    return r['cover']
    except Exception as e:
        pass
    return None

def netease_search(artist, album):
    """网易云 API"""
    q = urllib.parse.quote(f"{artist} {album}")
    url = f"https://music.163.com/api/search/get/web?csrf_token=&type=10&s={q}&offset=0&limit=5"
    headers = {**HEADERS, 'Referer': 'https://music.163.com/'}
    try:
        req = urllib.request.Request(url, headers=headers)
        data = json.loads(urlopen(url).read())
        if data.get('code') == 200 and data.get('result', {}).get('albumCount', 0) > 0:
            for r in data['result']['albums']:
                if 'picUrl' in r:
                    # 获取大图: ?param=600y600
                    pic = r['picUrl']
                    if '?' in pic:
                        pic = pic.split('?')[0]
                    return pic + '?param=600y600'
    except Exception as e:
        pass
    return None

def download_image(url, path):
    """下载图片"""
    try:
        data = urlopen(url, timeout=15).read()
        if len(data) < 1000:  # 太小的文件可能是占位图
            return False
        with open(path, 'wb') as f:
            f.write(data)
        return True
    except Exception:
        return False

# ---- Main ----

conn = sqlite3.connect(DB)
c = conn.cursor()

public_existing = set(os.listdir(PUBLIC_COVERS))

c.execute("SELECT album_id, album_name, artist FROM albums")
need = []
for row in c.fetchall():
    aid = row[0]
    found = any(f.startswith(f"{aid}-") for f in public_existing)
    if not found:
        need.append(row)

print(f"需下载: {len(need)} 张")
success = 0
failed = []

for i, (aid, aname, artist) in enumerate(need):
    fname = safe_filename(aid, artist, aname)
    path = os.path.join(PUBLIC_COVERS, fname)
    
    if os.path.exists(path):
        success += 1
        continue
    
    print(f"[{i+1}/{len(need)}] {aid} | {artist} - {aname}", end='')
    
    img_url = None
    
    # 1. iTunes
    img_url = itunes_search(artist, aname)
    if img_url:
        print(f" iTunes", end='')
    
    # 2. Deezer
    if not img_url:
        img_url = deezer_search(artist, aname)
        if img_url:
            print(f" Deezer", end='')
    
    # 3. 网易云
    if not img_url:
        img_url = netease_search(artist, aname)
        if img_url:
            print(f" 网易云", end='')
    
    if img_url:
        print(f" → {img_url[:60]}...", end='')
        if download_image(img_url, path):
            # Update DB
            new_url = f"/covers/{fname}"
            c.execute("UPDATE albums SET cover_image_url = ? WHERE album_id = ?", (new_url, aid))
            conn.commit()
            success += 1
            print(" ✅")
        else:
            print(" ❌ 下载失败")
            failed.append((aid, aname, artist))
    else:
        print(" ❌ 无来源")
        failed.append((aid, aname, artist))
    
    time.sleep(0.5)  # 限流

conn.close()
print(f"\n完成: {success}/{len(need)} 成功")
if failed:
    print(f"失败: {len(failed)}")
    for aid, aname, artist in failed:
        print(f"  {aid} | {artist} - {aname}")