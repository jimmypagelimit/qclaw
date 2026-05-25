#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
尝试从网易云下载苏紫旭 & The Paramecia - 悲歌欢唱 Lamenting in Delight 封面
"""
import urllib.request
import urllib.parse
import json
import os
import re

album_name = '悲歌欢唱 Lamenting in Delight'
artist = '苏紫旭'

covers_dir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\covers'
fname1 = '526-苏紫旭_&_The_Paramecia-悲歌欢唱_Lamenting_in_Delight.jpg'
fname2 = '181-苏紫旭_&_The_Paramecia-悲歌欢唱_Lamenting_in_Delight.jpg'

lines = []

lines.append('=== 尝试网易云 API ===')
lines.append(f'专辑: {album_name}')
lines.append(f'艺术家: {artist}')
lines.append('')

def download_image(url, save_path):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read()
            with open(save_path, 'wb') as f:
                f.write(data)
            return len(data)
    except Exception as e:
        return None

# 网易云搜索 API
lines.append('1. 搜索专辑...')
query = urllib.parse.quote(album_name)
url = f'https://music.163.com/api/search/get?s={query}&type=1&limit=5&offset=0'
try:
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://music.163.com/'
    })
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read())
        if 'result' in data and 'albums' in data['result'] and len(data['result']['albums']) > 0:
            for album in data['result']['albums']:
                album_name_api = album['name']
                artist_name = album['artist']['name']
                lines.append(f'  找到: {album_name_api} - {artist_name}')
                if 'picUrl' in album:
                    pic_url = album['picUrl']
                    lines.append(f'  封面 URL: {pic_url}')
                    # 下载封面
                    size = download_image(pic_url, os.path.join(covers_dir, fname1))
                    if size:
                        lines.append(f'  ✓ 已下载 (总表): {fname1} ({size} bytes)')
                        # 复制到 2026 表 ID
                        import shutil
                        shutil.copy(os.path.join(covers_dir, fname1), os.path.join(covers_dir, fname2))
                        lines.append(f'  ✓ 已复制 (2026表): {fname2}')
                        break
                    else:
                        lines.append(f'  ✗ 下载失败')
        else:
            lines.append('  ✗ 未找到专辑')
except Exception as e:
    lines.append(f'  ✗ 网易云 API 失败: {e}')

lines.append('')

# 检查文件是否存在
lines.append('=== 验证封面文件 ===')
fpath1 = os.path.join(covers_dir, fname1)
fpath2 = os.path.join(covers_dir, fname2)
if os.path.exists(fpath1):
    size1 = os.path.getsize(fpath1)
    lines.append(f'✓ 总表封面存在: {fname1} ({size1} bytes)')
else:
    lines.append(f'✗ 总表封面不存在: {fname1}')
if os.path.exists(fpath2):
    size2 = os.path.getsize(fpath2)
    lines.append(f'✓ 2026表封面存在: {fname2} ({size2} bytes)')
else:
    lines.append(f'✗ 2026表封面不存在: {fname2}')

lines.append('')
lines.append('=== 备选方案 ===')
lines.append('如果网易云也没有，可以：')
lines.append('1. 用 opencli browser 搜索网易云网页版')
lines.append('2. 手动从 RYM 截图')
lines.append('3. 暂时留空 cover_image_url，后续补')

output = '\n'.join(lines)

with open(r'C:\Users\qujt\.qclaw\workspace\download_cover_wangyi.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print('Done, saved to download_cover_wangyi.txt')
