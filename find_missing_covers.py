#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, urllib.request, os, shutil

cover_dir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\covers'

# jody积融 - Is It Gonna Happen Again?
print('=== jody积融 - Is It Gonna Happen Again? ===')
url = 'https://api.deezer.net/search/album?q=jody+Is+It+Gonna+Happen+Again'
try:
    data = json.loads(urllib.request.urlopen(url, timeout=10).read())
    if data.get('data'):
        for a in data['data']:
            print('Found:', a['artist']['name'], '-', a['title'])
            print('Cover:', a['cover_big'])
            # Download
            cover_url = a['cover_big']
            img = urllib.request.urlopen(cover_url, timeout=10).read()
            c1 = os.path.join(cover_dir, '533-jody_-Is_It_Gonna_Happen_Again.jpg')
            c2 = os.path.join(cover_dir, '189-jody_-Is_It_Gonna_Happen_Again.jpg')
            with open(c1, 'wb') as f:
                f.write(img)
            shutil.copy2(c1, c2)
            print('Downloaded:', len(img), 'bytes')
    else:
        print('Not found on Deezer')
except Exception as e:
    print('Deezer failed:', e)

print()

# 谢甜柚 - 脱轨
print('=== 谢甜柚 - 脱轨 ===')
# Try MusicBrainz cover art archive
url2 = 'https://musicbrainz.org/ws/2/release/?query=artist:谢甜柚+AND+release:脱轨&fmt=json&limit=5'
try:
    req = urllib.request.Request(url2, headers={'User-Agent': 'XiaoFei/1.0 (jim@example.com)'})
    data2 = json.loads(urllib.request.urlopen(req, timeout=10).read())
    if data2.get('releases'):
        for r in data2['releases']:
            print('Found:', r['title'], 'id:', r['id'])
            # Try Cover Art Archive
            mbid = r['id']
            cover_url = f'https://coverartarchive.org/release/{mbid}/front'
            try:
                img = urllib.request.urlopen(cover_url, timeout=10).read()
                c1 = os.path.join(cover_dir, '534-谢甜柚-脱轨.jpg')
                c2 = os.path.join(cover_dir, '190-谢甜柚-脱轨.jpg')
                with open(c1, 'wb') as f:
                    f.write(img)
                shutil.copy2(c1, c2)
                print('Downloaded from CAA:', len(img), 'bytes')
            except:
                print('CAA not available')
    else:
        print('No results from MusicBrainz')
except Exception as e:
    print('MusicBrainz failed:', e)

print()
print('=== Done ===')
