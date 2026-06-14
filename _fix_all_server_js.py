#!/usr/bin/env python3
"""全面修复 dist/server.js 中所有 total_listen_count 引用"""
import re, os

fpath = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\dist\server.js'
with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()
original = content
fixed = 0

# 1. /api/albums sortMap listen（位置 6563 附近，已修复过则跳过）
old = "'listen': 'total_listen_count',"
if old in content:
    content = content.replace(old, "'listen': '(SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id)',")
    fixed += 1
    print('[1] /api/albums sortMap listen')

# 2. /api/albums sortCol fallback（位置 6935 附近）
old = "|| 'total_listen_count';"
if old in content:
    content = content.replace(old, "|| '(SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id)';")
    fixed += 1
    print('[2] /api/albums sortCol fallback')

# 3. /api/artists sortMap listen（位置 11365 附近）
old = "'listen': 'total_listen_count',"
if old in content:
    # artists 表的 listen count 需要 JOIN albums
    content = content.replace(old, "'listen': '(SELECT COUNT(*) FROM listen_history lh JOIN albums a2 ON lh.album_id = a2.album_id WHERE a2.artist_id = a.artist_id)',")
    fixed += 1
    print('[3] /api/artists sortMap listen')

# 4. /api/artists SELECT total_listen_count（位置 11717 附近）
old = "        total_listen_count,\n"
if old in content:
    content = content.replace(old, "        (SELECT COUNT(*) FROM listen_history lh JOIN albums a2 ON lh.album_id = a2.album_id WHERE a2.artist_id = a.artist_id) as computed_listen,\n")
    fixed += 1
    print('[4] /api/artists SELECT total_listen_count')

# 5. ORDER BY total_listen_count DESC LIMIT（位置 12227 附近，封面查询）
old = "ORDER BY total_listen_count DESC LIMIT"
if old in content:
    content = content.replace(old, "ORDER BY (SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id) DESC LIMIT")
    fixed += 1
    print('[5] ORDER BY total_listen_count DESC')

# 6. 清除 stats 接口中的 SUM(total_listen_count)
old = "'SELECT COALESCE(SUM(total_listen_count), 0) as total FROM albums'"
if old in content:
    content = content.replace(old, "'SELECT COUNT(*) as total FROM listen_history'")
    fixed += 1
    print('[6] stats SUM(total_listen_count)')

# 7. 清除 stats topAlbum 中的 ORDER BY total_listen_count
old = "'SELECT * FROM albums ORDER BY total_listen_count DESC LIMIT 1'"
if old in content:
    content = content.replace(old, "`SELECT a.*, COUNT(lh.id) as cnt FROM albums a LEFT JOIN listen_history lh ON a.album_id = lh.album_id GROUP BY a.album_id ORDER BY cnt DESC LIMIT 1`")
    fixed += 1
    print('[7] stats topAlbum ORDER BY')

# 8. /api/artist/:name ORDER BY total_listen_count（位置约 12000 附近）
old = "ORDER BY total_listen_count DESC"
if old in content:
    content = content.replace(old, "ORDER BY (SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id) DESC")
    fixed += 1
    print('[8] /api/artist/:name ORDER BY')

# 9. /api/top 非年份 ORDER BY total_listen_count
old = "'SELECT * FROM albums ORDER BY total_listen_count DESC LIMIT ?',"
if old in content:
    content = content.replace(old, "'SELECT a.*, COUNT(lh.id) as cnt FROM albums a LEFT JOIN listen_history lh ON a.album_id = lh.album_id GROUP BY a.album_id ORDER BY cnt DESC LIMIT ?',")
    fixed += 1
    print('[9] /api/top non-year ORDER BY')

# 检查剩余
remaining = [m.start() for m in re.finditer(r'total_listen_count', content)]
print(f'\n修复完成：{fixed} 处')
print(f'剩余引用：{len(remaining)} 处')
if remaining:
    print('剩余位置：', remaining[:10])

# 保存
with open(fpath, 'w', encoding='utf-8') as f:
    f.write(content)
print(f'已保存：{fpath}')
print(f'字符变化：{len(original)} -> {len(content)}')
