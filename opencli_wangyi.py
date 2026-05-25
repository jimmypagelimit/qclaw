#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 opencli browser 搜索网易云网页版，获取苏紫旭专辑封面
"""
import subprocess
import time
import os
import urllib.parse

album_name = '悲歌欢唱 Lamenting in Delight'
artist = '苏紫旭'

covers_dir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\covers'
fname1 = '526-苏紫旭_&_The_Paramecia-悲歌欢唱_Lamenting_in_Delight.jpg'
fname2 = '181-苏紫旭_&_The_Paramecia-悲歌欢唱_Lamenting_in_Delight.jpg'

lines = []

lines.append('=== 使用 opencli browser 搜索网易云 ===')
lines.append(f'专辑: {album_name}')
lines.append(f'艺术家: {artist}')
lines.append('')

# 1. 打开网易云搜索页面
search_query = urllib.parse.quote(f'{artist} {album_name}')
wangyi_url = f'https://music.163.com/#/search/m/?s={search_query}&type=1'

lines.append(f'1. 打开网易云搜索页面...')
lines.append(f'  URL: {wangyi_url}')

try:
    # 使用 opencli browser work open 打开页面
    result = subprocess.run(
        ['opencli', 'browser', 'work', 'open', wangyi_url],
        capture_output=True,
        text=True,
        timeout=10
    )
    lines.append(f'  结果: {result.stdout}')
    if result.returncode != 0:
        lines.append(f'  ✗ 失败: {result.stderr}')
except Exception as e:
    lines.append(f'  ✗ 异常: {e}')

lines.append('')

# 2. 等待页面加载
lines.append('2. 等待页面加载 (5秒)...')
time.sleep(5)
lines.append('  等待完成')
lines.append('')

# 3. 截图查看搜索结果
lines.append('3. 截图查看搜索结果...')
try:
    result2 = subprocess.run(
        ['opencli', 'browser', 'work', 'screenshot', '--output', 'wangyi_search.png'],
        capture_output=True,
        text=True,
        timeout=10
    )
    lines.append(f'  截图保存: wangyi_search.png')
    lines.append(f'  结果: {result2.stdout}')
except Exception as e:
    lines.append(f'  ✗ 截图失败: {e}')

lines.append('')
lines.append('=== 说明 ===')
lines.append('由于网易云页面是 JS 渲染的，需要：')
lines.append('1. 查看 wangyi_search.png 截图，确认是否找到专辑')
lines.append('2. 如果找到，手动点击专辑，进入详情页')
lines.append('3. 右键封面 → 另存为，保存到 covers/ 目录')
lines.append('')
lines.append('=== 备选方案 ===')
lines.append('如果 opencli browser 无法找到，可以：')
lines.append('1. 手动在浏览器中打开网易云，搜索专辑')
lines.append('2. 右键封面 → 另存为')
lines.append('3. 保存为 covers/526-苏紫旭_&_The_Paramecia-悲歌欢唱_Lamenting_in_Delight.jpg')
lines.append('4. 同时复制到 covers/181-...jpg')

output = '\n'.join(lines)

with open(r'C:\Users\qujt\.qclaw\workspace\opencli_wangyi.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print('Done, saved to opencli_wangyi.txt')
print('Please check wangyi_search.png screenshot')
