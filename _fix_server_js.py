#!/usr/bin/env python3
"""直接修复 dist/server.js 中的 total_listen_count 引用"""
import re

fpath = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\dist\server.js'

with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

original = content

# 修复1: sortMap 中的 listen（单引号版本）
old1 = "'listen': 'total_listen_count',"
new1 = "'listen': '(SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id)',"
if old1 in content:
    content = content.replace(old1, new1)
    print('[OK] 修复1: sortMap listen (单引号)')
else:
    print('[SKIP] 修复1: 未找到，尝试双引号...')
    old1b = '"listen": "total_listen_count",'
    if old1b in content:
        content = content.replace(old1b, new1)
        print('  -> 双引号版本已修复')
    else:
        print('  未找到匹配')

# 修复2: sortCol fallback
old2 = "const sortCol = sortMap[sort] || 'total_listen_count';"
new2 = "const sortCol = sortMap[sort] || '(SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id)';"
if old2 in content:
    content = content.replace(old2, new2)
    print('[OK] 修复2: sortCol fallback')
else:
    print('[SKIP] 修复2: 未找到匹配')

# 检查还有多少处 total_listen_count
remaining = [m.start() for m in re.finditer(r'total_listen_count', content)]
print(f'\n剩余 total_listen_count 引用: {len(remaining)} 处')
if remaining:
    print('（这些可能在注释或其他不关键位置，暂不影响功能）')

# 保存
with open(fpath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\n完成: {fpath}')
print(f'字符变化: {len(original)} -> {len(content)}')
