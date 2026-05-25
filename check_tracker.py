#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

tracker_dir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker'

print('=== album-tracker 目录结构 ===')
print()

# 读文件列表
if os.path.exists(tracker_dir):
    files = os.listdir(tracker_dir)
    for f in sorted(files)[:30]:
        fpath = os.path.join(tracker_dir, f)
        if os.path.isdir(fpath):
            print(f'[DIR]  {f}')
        else:
            size = os.path.getsize(fpath)
            print(f'[FILE] {f} ({size} bytes)')
else:
    print('目录不存在')

print()
print('=== 读取 README.md ===')
readme_path = os.path.join(tracker_dir, 'README.md')
if os.path.exists(readme_path):
    with open(readme_path, 'r', encoding='utf-8') as f:
        print(f.read()[:2000])
else:
    print('README.md 不存在')

print()
print('=== 读取 package.json ===')
pkg_path = os.path.join(tracker_dir, 'package.json')
if os.path.exists(pkg_path):
    with open(pkg_path, 'r', encoding='utf-8') as f:
        print(f.read()[:1000])
