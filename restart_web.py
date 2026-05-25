#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重启 album-tracker Web 服务
1. 停止现有 node 进程
2. 启动 Web 服务（node dist/server.js）
3. 验证服务可访问
"""
import subprocess
import time
import sys

lines = []

lines.append('=== 重启 album-tracker Web 服务 ===')
lines.append('')

# 1. 停止现有进程
lines.append('1. 停止现有 node 进程...')
try:
    result = subprocess.run(
        ['taskkill', '/F', '/IM', 'node.exe'],
        capture_output=True,
        text=True,
        timeout=5
    )
    lines.append(f'  结果: {result.stdout.strip()}')
    if result.returncode != 0 and '没有找到进程' not in result.stderr:
        lines.append(f'  警告: {result.stderr.strip()}')
except Exception as e:
    lines.append(f'  ✗ 异常: {e}')

lines.append('')

# 2. 等待进程完全停止
lines.append('2. 等待进程完全停止 (3秒)...')
time.sleep(3)
lines.append('  等待完成')
lines.append('')

# 3. 启动 Web 服务
lines.append('3. 启动 Web 服务...')
album_tracker_dir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker'

try:
    # 使用 subprocess.Popen 后台启动
    process = subprocess.Popen(
        ['node', 'dist/server.js'],
        cwd=album_tracker_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL
    )
    lines.append(f'  ✓ 已启动 Web 服务 (PID: {process.pid})')
except Exception as e:
    lines.append(f'  ✗ 启动失败: {e}')
    sys.exit(1)

lines.append('')

# 4. 等待服务启动
lines.append('4. 等待服务启动 (5秒)...')
time.sleep(5)
lines.append('  等待完成')
lines.append('')

# 5. 验证服务可访问
lines.append('5. 验证服务可访问...')
try:
    import urllib.request
    with urllib.request.urlopen('http://localhost:3456', timeout=5) as response:
        if response.status == 200:
            lines.append('  ✓ Web 服务可访问 (http://localhost:3456)')
        else:
            lines.append(f'  ✗ 状态码异常: {response.status}')
except Exception as e:
    lines.append(f'  ✗ 无法访问: {e}')

lines.append('')
lines.append('=== 重启完成 ===')
lines.append('')
lines.append('新添加的专辑（苏紫旭 & The Paramecia - 悲歌欢唱 Lamenting in Delight）')
lines.append('现在应该可以在 http://localhost:3456 看到。')

output = '\n'.join(lines)

with open(r'C:\Users\qujt\.qclaw\workspace\restart_web.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print('Done, saved to restart_web.txt')
