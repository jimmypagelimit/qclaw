#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载 Car Seat Headrest - Twin Fantasy (2018 重录版) 封面
"""
import urllib.request
import json
import os

print('=== 搜索 Twin Fantasy 封面 ===')
print()

# iTunes Search API
search_url = "https://itunes.apple.com/search?term=Car+Seat+Headrest+Twin+Fantasy&entity=album&limit=10"

try:
    req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode('utf-8'))
    
    print(f'找到 {len(data["results"])} 个结果')
    print()
    
    # 找 2018 年版 Twin Fantasy
    found = False
    for album in data['results']:
        artist = album.get('artistName', '')
        album_name = album.get('collectionName', '')
        year = album.get('releaseDate', '')[:4]
        
        print(f'{artist} - {album_name} ({year})')
        
        # 匹配 Twin Fantasy 2018
        if 'Twin Fantasy' in album_name and 'Car Seat Headrest' in artist and year == '2018':
            art_url = album.get('artworkUrl100', '')
            art_url_hq = art_url.replace('100x100bb', '600x600bb')
            
            print(f'→ 匹配 2018 版!')
            print(f'  Cover URL: {art_url_hq}')
            
            # 下载封面
            cover_dir = r'G:\原创计划\music\covers'
            os.makedirs(cover_dir, exist_ok=True)
            cover_path = os.path.join(cover_dir, '323-Car_Seat_Headrest-Twin_Fantasy.jpg')
            
            print(f'  下载到: {cover_path}')
            urllib.request.urlretrieve(art_url_hq, cover_path)
            
            file_size = os.path.getsize(cover_path)
            print(f'  ✓ 下载成功! 文件大小: {file_size} bytes')
            found = True
            break
    
    if not found:
        print('未找到 2018 版 Twin Fantasy')
    
except Exception as e:
    print(f'错误: {e}')
    import traceback
    traceback.print_exc()

print()
print('Done')
