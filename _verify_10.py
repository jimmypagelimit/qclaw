#!/usr/bin/env python3
"""验证10张专辑信息"""
import urllib.request, json, time

time.sleep(1)

albums_to_check = [602, 601, 600, 599, 598, 597, 596, 595, 594, 593]
print('=== 验证10张专辑 ===\n')
missing = 0
for aid in albums_to_check:
    try:
        r = urllib.request.urlopen(f'http://127.0.0.1:3456/api/albums/{aid}', timeout=5)
        d = json.loads(r.read())
        name = d.get('album_name','')
        artist = d.get('artist','')
        cover = d.get('cover_image_url','')
        company = d.get('release_company','')
        genre = d.get('genre','')
        issues = []
        if not cover: issues.append('cover')
        if not company: issues.append('company')
        if not genre: issues.append('genre')
        if issues:
            print(f'ID={aid} {artist} - {name}: MISSING {", ".join(issues)}')
            missing += 1
        else:
            print(f'ID={aid} {artist} - {name}: OK')
    except Exception as e:
        print(f'ID={aid}: ERROR - {e}')
        missing += 1

if missing == 0:
    print('\n10/10 全部完成!')
else:
    print(f'\n{missing}/10 还有缺失字段')
