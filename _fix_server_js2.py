#!/usr/bin/env python3
"""修复 dist/server.js 中 /api/artists 的两处 total_listen_count 引用"""
import re

fpath = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\dist\server.js'

with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

original = content

# 修复1: /api/artists 的 sortMap listen 键值
# 把 'total_listen_count' 换成 artist 收听次数的子查询
old1 = "'listen': 'total_listen_count',"
new1 = "'listen': '(SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id IN (SELECT album_id FROM albums WHERE artist = a.name))',"
if old1 in content:
    content = content.replace(old1, new1)
    print('[OK] 修复1: /api/artists sortMap listen')
else:
    print('[SKIP] 修复1: 未找到匹配，搜索中...')
    # 搜索 listen 键值
    for m in re.finditer(r"listen.*?:.*?',", content):
        start = max(0, m.start()-50)
        end = min(len(content), m.end()+20)
        print(f'  找到: ...{content[start:end]}...')

# 修复2: /api/artists 的 SELECT total_listen_count
# 替换成子查询
old2 = "        total_listen_count,\n"
# 注意：这个 old2 可能匹配多处，需要限定在 artists 查询附近
# 更安全的做法：搜索 "FROM artists" 前面的 total_listen_count
pattern2 = r'(SELECT \n        artist_id,\n        name as artist,\n        )total_listen_count(\n        avg_rating)'
new2 = r'\1(SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id IN (SELECT album_id FROM albums WHERE artist = a.name)) as computed_listen_count\2'
if re.search(pattern2, content):
    content = re.sub(pattern2, new2, content)
    print('[OK] 修复2: /api/artists SELECT total_listen_count')
else:
    print('[SKIP] 修复2: 未找到匹配')

# 修复3: /api/artists 的 ORDER BY sortCol（如果 sortCol 还引用 total_listen_count）
# sortCol fallback 已经在 _fix_server_js.py 里修复过了，检查是否还有漏网之鱼
if "|| 'total_listen_count'" in content:
    content = content.replace("|| 'total_listen_count'", "|| '(SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id)'")
    print('[OK] 修复3: 残留 sortCol fallback')
else:
    print('[OK] 修复3: 无残留 fallback')

# 检查还有多少处 total_listen_count
remaining = [(m.start(), m.group()) for m in re.finditer(r'total_listen_count', content)]
print(f'\n剩余 total_listen_count 引用: {len(remaining)} 处')
for pos, match in remaining[:5]:
    start = max(0, pos-60)
    end = min(len(content), pos+30)
    print(f'  位置 {pos}: ...{repr(content[start:end])}...')

# 保存
with open(fpath, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\n完成: {fpath}')
print(f'字符变化: {len(original)} -> {len(content)}')
