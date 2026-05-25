#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用 Deezer API 下载 Car Seat Headrest - Twin Fantasy (2018) 封面
"""
import urllib.request
import json
import os

print('=== 用 Deezer 搜索 Twin Fantasy (2018) ===')
print()

# Deezer Search API
search_url = "https://api.deezer.com/search/album?q=Car+Seat+Headrest+Twin+Fantasy&limit=10"

try:
    req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode('utf-8'))
    
    print(f'找到 {len(data.get("data", []))} 个结果')
    print()
    
    found = False
    for album in data.get('data', []):
        artist = album.get('artist', {}).get('name', '')
        album_name = album.get('title', '')
        album_id = album.get('id', '')
        cover_url = album.get('cover_big', '') or album.get('cover_xl', '')
        
        print(f'{artist} - {album_name} (ID: {album_id})')
        
        # 匹配 Twin Fantasy
        if 'Twin Fantasy' in album_name and 'Car Seat Headrest' in artist:
            print(f'→ 匹配!')
            print(f'  Cover URL: {cover_url}')
            
            # 下载封面
            cover_dir = r'G:\原创计划\music\covers'
            os.makedirs(cover_dir, exist_ok=True)
            cover_path = os.path.join(cover_dir, '323-Car_Seat_Headrest-Twin_Fantasy.jpg')
            
            print(f'  下载到: {cover_path}')
            urllib.request.urlretrieve(cover_url, cover_path)
            
            file_size = os.path.getsize(cover_path)
            print(f'  ✓ 下载成功! 文件大小: {file_size} bytes')
            found = True
            break
    
    if not found:
        print('未找到匹配的专辑')
    
except Exception as e:
    print(f'错误: {e}')
    import traceback
    traceback.print_exc()

print()
print('Done')
