#!/usr/bin/env python3
"""下载最后3张缺失封面"""
import urllib.request, json, os, time, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
PUBLIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'public', 'covers')

HEADERS = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com/'}

def sanitize(s):
    return re.sub(r'[\\/:*?"<>|,]', '_', str(s).strip())

def dl(url, path):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = urllib.request.urlopen(req, timeout=15).read()
        if len(data) > 2000:
            with open(path, 'wb') as f:
                f.write(data)
            return True
    except Exception as e:
        print(f"   下载失败: {e}")
    return False

def deezer_search(q):
    url = f'https://api.deezer.com/search/album?q={urllib.parse.quote(q)}&limit=5'
    data = json.loads(urllib.request.urlopen(url, timeout=10).read())
    return data.get('data', [])

def netease_search(q):
    url = f'https://music.163.com/api/search/get/web?csrf_token=&type=10&s={urllib.parse.quote(q)}&offset=0&limit=5'
    req = urllib.request.Request(url, headers=HEADERS)
    data = json.loads(urllib.request.urlopen(req, timeout=10).read())
    if data.get('code') == 200:
        return data.get('result', {}).get('albums', [])
    return []

# 486: Annabelle Dinda - Some Things Never Leave
print("=== 486: Annabelle Dinda - Some Things Never Leave ===")
results = deezer_search('Annabelle Dinda Some Things Never Leave')
for r in results:
    print(f"  Deezer: {r.get('title')} - {r.get('artist',{}).get('name')}")
    if 'cover_big' in r:
        fname = f"486-Annabelle_Dinda-Some_Things_Never_Leave.jpg"
        path = os.path.join(PUBLIC, fname)
        if dl(r['cover_big'], path):
            print(f"  ✅ 已下载: {fname}")

# 490: Otto Benson - Peanut
print("\n=== 490: Otto Benson - Peanut ===")
results = deezer_search('Otto Benson Peanut')
for r in results:
    print(f"  Deezer: {r.get('title')} - {r.get('artist',{}).get('name')}")
    if 'cover_big' in r:
        fname = f"490-Otto_Benson-Peanut.jpg"
        path = os.path.join(PUBLIC, fname)
        if dl(r['cover_big'], path):
            print(f"  ✅ 已下载: {fname}")

# 139: 苍蝇 - The Fly II
print("\n=== 139: 苍蝇 - The Fly II ===")
results = netease_search('苍蝇 The Fly II')
for r in results:
    print(f"  网易云: {r.get('name')}")
    if 'picUrl' in r:
        pic = r['picUrl'].split('?')[0] + '?param=600y600'
        fname = f"139-苍蝇-The_Fly_II.jpg"
        path = os.path.join(PUBLIC, fname)
        if dl(pic, path):
            print(f"  ✅ 已下载: {fname}")

results = deezer_search('苍蝇 The Fly II')
for r in results:
    print(f"  Deezer: {r.get('title')} - {r.get('artist',{}).get('name')}")
    if 'cover_big' in r:
        fname = f"139-苍蝇-The_Fly_II.jpg"
        path = os.path.join(PUBLIC, fname)
        if dl(r['cover_big'], path):
            print(f"  ✅ 已下载: {fname}")