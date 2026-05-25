#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

tracker_dir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker'

lines = []
lines.append('=== album-tracker 项目文档 ===')
lines.append('')

# 读 README.md
readme_path = os.path.join(tracker_dir, 'README.md')
if os.path.exists(readme_path):
    lines.append('--- README.md ---')
    with open(readme_path, 'r', encoding='utf-8') as f:
        lines.append(f.read())
    lines.append('')

# 读 PROJECT.md
proj_path = os.path.join(tracker_dir, 'PROJECT.md')
if os.path.exists(proj_path):
    lines.append('--- PROJECT.md ---')
    with open(proj_path, 'r', encoding='utf-8') as f:
        lines.append(f.read())
    lines.append('')

# 读 package.json
pkg_path = os.path.join(tracker_dir, 'package.json')
if os.path.exists(pkg_path):
    lines.append('--- package.json ---')
    with open(pkg_path, 'r', encoding='utf-8') as f:
        lines.append(f.read())
    lines.append('')

# 列出 dist/ 目录
dist_dir = os.path.join(tracker_dir, 'dist')
if os.path.exists(dist_dir):
    lines.append('--- dist/ 目录 ---')
    for f in os.listdir(dist_dir)[:20]:
        lines.append(f)
    lines.append('')

output = '\n'.join(lines)

with open(r'C:\Users\qujt\.qclaw\workspace\album_tracker_docs.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print('Done, saved to album_tracker_docs.txt')
print(f'Total length: {len(output)} chars')
