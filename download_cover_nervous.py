#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载 Car Seat Headrest - Nervous Young Man 封面
"""
import urllib.request
import urllib.parse
import json
import os
import shutil

album_name = 'Nervous Young Man'
artist = 'Car Seat Headrest'

covers_dir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\covers'
fname = '183-Car_Seat_Headrest-Nervous_Young_Man.jpg'

lines = []

def download_image(url, save_path):
    """下载图片到指定路径"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read()
            with open(save_path, 'wb') as f:
                f.write(data)
            return len(data)
    except Exception as e:
        return None

lines.append('=== 下载封面 ===')
lines.append(f'专辑: {album_name}')
lines.append(f'艺术家: {artist}')
lines.append('')

# 方法1：iTunes Search API
lines.append('1. 尝试 iTunes Search API...')
query = urllib.parse.quote(f'{artist} {album_name}')
itunes_url = f'https://itunes.apple.com/search?term={query}&entity=album&limit=5'
try:
    with urllib.request.urlopen(itunes_url, timeout=10) as response:
        data = json.loads(response.read())
        if data['resultCount'] > 0:
            for result in data['results']:
                if 'artworkUrl100' in result:
                    artwork = result['artworkUrl100'].replace('100x100bb.jpg', '600x600bb.jpg')
                    lines.append(f'  找到封面: {artwork}')
                    # 下载
                    size = download_image(artwork, os.path.join(covers_dir, fname))
                    if size:
                        lines.append(f'  ✓ 已下载: {fname} ({size} bytes)')
                        break
                    else:
                        lines.append(f'  ✗ 下载失败')
        else:
            lines.append('  ✗ 未找到专辑')
except Exception as e:
    lines.append(f'  ✗ iTunes API 失败: {e}')

lines.append('')

# 方法2：Deezer API
lines.append('2. 尝试 Deezer API...')
query_dz = urllib.parse.quote(f'{artist} {album_name}')
deezer_url = f'https://api.deezer.com/search/album?q={query_dz}&limit=5'
try:
    with urllib.request.urlopen(deezer_url, timeout=10) as response:
        data = json.loads(response.read())
        if 'data' in data and len(data['data']) > 0:
            for result in data['data']:
                if 'cover_big' in result:
                    cover_url = result['cover_big']
                    lines.append(f'  找到封面: {cover_url}')
                    size = download_image(cover_url, os.path.join(covers_dir, fname))
                    if size:
                        lines.append(f'  ✓ 已下载: {fname} ({size} bytes)')
                        break
                    else:
                        lines.append(f'  ✗ 下载失败')
        else:
            lines.append('  ✗ 未找到专辑')
except Exception as e:
    lines.append(f'  ✗ Deezer API 失败: {e}')

lines.append('')

# 检查文件是否存在
lines.append('=== 验证封面文件 ===')
fpath = os.path.join(covers_dir, fname)
if os.path.exists(fpath):
    size = os.path.getsize(fpath)
    lines.append(f'✓ 封面存在: {fname} ({size} bytes)')
else:
    lines.append(f'✗ 封面不存在: {fname}')

output = '\n'.join(lines)

with open(r'C:\Users\qujt\.qclaw\workspace\download_cover_nervous.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print('Done, saved to download_cover_nervous.txt')
