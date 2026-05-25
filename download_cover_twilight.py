#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载 The Twilight Sad - It's the Long Goodbye 专辑封面
"""
import json
import urllib.request
import os
import shutil

lines = []

lines.append('=== 下载封面 ===')
lines.append('专辑: It\'s the Long Goodbye')
lines.append('艺术家: The Twilight Sad')
lines.append('')

# 封面路径（正确路径）
cover_dir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\covers'
cover1 = os.path.join(cover_dir, '513-The_Twilight_Sad-It_s_the_Long_Goodbye.jpg')
cover2 = os.path.join(cover_dir, '114-The_Twilight_Sad-It_s_the_Long_Goodbye.jpg')

lines.append(f'封面目录: {cover_dir}')
lines.append('')

# 检查封面是否已存在
lines.append('封面不存在，开始下载...')
lines.append('')

# 1. 尝试 iTunes Search API
lines.append('1. 尝试 iTunes Search API...')
itunes_url = 'https://itunes.apple.com/search?term=The+Twilight+Sad+It+s+the+Long+Goodbye&entity=album&limit=5'
try:
    response = urllib.request.urlopen(itunes_url, timeout=10)
    data = json.loads(response.read().decode('utf-8'))
    if data['resultCount'] > 0:
        for result in data['results']:
            if 'artworkUrl100' in result:
                artwork_url = result['artworkUrl100'].replace('100x100bb', '600x600bb')
                lines.append(f'  找到封面: {artwork_url}')
                
                # 下载封面
                img_data = urllib.request.urlopen(artwork_url, timeout=10).read()
                with open(cover1, 'wb') as f:
                    f.write(img_data)
                lines.append(f'  ✓ 已下载: {os.path.basename(cover1)} ({len(img_data)} bytes)')
                
                # 复制到第二个位置
                shutil.copy2(cover1, cover2)
                lines.append(f'  ✓ 已复制: {os.path.basename(cover2)}')
                break
    else:
        lines.append('  ✗ iTunes API 未找到此专辑')
except Exception as e:
    lines.append(f'  ✗ iTunes API 错误: {e}')

lines.append('')

# 2. 尝试 Deezer API
lines.append('2. 尝试 Deezer API...')
deezer_url = 'https://api.deezer.com/search/album?q=The+Twilight+Sad+It+s+the+Long+Goodbye'
try:
    response = urllib.request.urlopen(deezer_url, timeout=10)
    data = json.loads(response.read().decode('utf-8'))
    if 'data' in data and len(data['data']) > 0:
        album = data['data'][0]
        if 'cover_big' in album:
            cover_url = album['cover_big']
            lines.append(f'  找到封面: {cover_url}')
            
            # 下载封面
            img_data = urllib.request.urlopen(cover_url, timeout=10).read()
            with open(cover1, 'wb') as f:
                f.write(img_data)
            lines.append(f'  ✓ 已下载: {os.path.basename(cover1)} ({len(img_data)} bytes)')
            
            # 复制到第二个位置
            shutil.copy2(cover1, cover2)
            lines.append(f'  ✓ 已复制: {os.path.basename(cover2)}')
    else:
        lines.append('  ✗ Deezer API 未找到此专辑')
except Exception as e:
    lines.append(f'  ✗ Deezer API 错误: {e}')

lines.append('')
lines.append('=== 验证封面文件 ===')
if os.path.exists(cover1):
    size1 = os.path.getsize(cover1)
    lines.append(f'✓ 封面1存在: {os.path.basename(cover1)} ({size1} bytes)')
else:
    lines.append(f'✗ 封面1不存在: {os.path.basename(cover1)}')

if os.path.exists(cover2):
    size2 = os.path.getsize(cover2)
    lines.append(f'✓ 封面2存在: {os.path.basename(cover2)} ({size2} bytes)')
else:
    lines.append(f'✗ 封面2不存在: {os.path.basename(cover2)}')

output = '\n'.join(lines)

with open(r'C:\Users\qujt\.qclaw\workspace\download_cover_twilight.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print('Done, saved to download_cover_twilight.txt')
