#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查张悬封面文件是否存在（繁体 vs 简体）
"""
import os

covers_dir = r'G:\原创计划\covers'

lines = []
lines.append('=== 检查张悬封面文件 ===')
lines.append('')

# 检查繁体文件名（当前 cover_image_url 指向的）
files_to_check = [
    ('448-張懸_[Deserts_Chang]-城市.jpg', 'id=39 (城市)'),
    ('449-張懸_[Deserts_Chang]-神的遊戲_Games_We_Play.jpg', 'id=40 (神的游戏)'),
    # 简体文件名（应该改成的）
    ('168-张悬-城市.jpg', '简体版本 (城市)'),
    ('6-张悬-神的游戏.jpg', '简体版本 (神的游戏)'),
]

for fname, desc in files_to_check:
    fpath = os.path.join(covers_dir, fname)
    exists = os.path.exists(fpath)
    status = 'OK 存在' if exists else 'NOT 不存在'
    lines.append(f'{status}  {fname}  ({desc})')
    if exists:
        size = os.path.getsize(fpath)
        lines.append(f'   文件大小: {size} bytes')
    lines.append('')

lines.append('=== 列出所有张悬相关封面 ===')
if os.path.exists(covers_dir):
    all_files = os.listdir(covers_dir)
    zx_files = [f for f in all_files if '张悬' in f or '張懸' in f or 'Deserts' in f]
    if zx_files:
        lines.append(f'找到 {len(zx_files)} 个文件:')
        for f in sorted(zx_files):
            fpath = os.path.join(covers_dir, f)
            size = os.path.getsize(fpath) if os.path.exists(fpath) else 0
            lines.append(f'  {f} ({size} bytes)')
    else:
        lines.append('未找到张悬相关封面文件')
else:
    lines.append(f'封面目录不存在: {covers_dir}')

output = '\n'.join(lines)

with open(r'C:\Users\qujt\.qclaw\workspace\zx_covers_check.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print('Done, saved to zx_covers_check.txt')
