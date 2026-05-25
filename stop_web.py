#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
停止 album-tracker Web 服务（Windows）
"""
import subprocess
import time
import urllib.request

lines = []

lines.append('=== 停止 album-tracker Web 服务 ===')
lines.append('')

# 1. 停止所有 node 进程
lines.append('1. 停止所有 node 进程...')
result = subprocess.run(
    ['taskkill', '/F', '/IM', 'node.exe'],
    capture_output=True,
    text=True
)
lines.append(f'  结果: {result.stdout.strip()}')
if result.stderr:
    lines.append(f'  错误: {result.stderr.strip()}')
lines.append('')

# 2. 等待进程完全停止
lines.append('2. 等待进程完全停止 (3秒)...')
time.sleep(3)
lines.append('  等待完成')
lines.append('')

# 3. 验证端口 3456 是否已释放
lines.append('3. 验证端口 3456...')
try:
    urllib.request.urlopen('http://localhost:3456', timeout=2)
    lines.append('  ⚠ 端口 3456 仍被占用')
except:
    lines.append('  ✓ 端口 3456 已释放')

lines.append('')
lines.append('=== 停止完成 ===')

output = '\n'.join(lines)

with open(r'C:\Users\qujt\.qclaw\workspace\stop_web.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print('Done, saved to stop_web.txt')
