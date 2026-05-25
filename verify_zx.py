#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证张悬专辑统一是否成功
"""
import sqlite3
import os

db = r'G:\原创计划\music'
if os.path.isdir(db):
    db = os.path.join(db, 'music')

conn = sqlite3.connect(db)
c = conn.cursor()

lines = []

lines.append('=== 验证 albums_2026 表更新结果 ===')
c.execute("SELECT album_id, album_name, artist, cover_image_url FROM albums_2026 WHERE album_name LIKE '%城市%' OR album_name LIKE '%神的游戏%' ORDER BY album_id")
rows = c.fetchall()
for r in rows:
    lines.append(f'  id={r[0]} | {r[1]}')
    lines.append(f'    artist={r[2]}')
    lines.append(f'    cover={r[3]}')
lines.append('')

lines.append('=== 检查是否有繁体残留 ===')
# 检查 artist 字段
c.execute("SELECT COUNT(*) FROM albums_2026 WHERE artist LIKE '%張懸%'")
cnt1 = c.fetchone()[0]
lines.append(f'  artist 含繁体: {cnt1} 条')
# 检查 album_name 字段
c.execute("SELECT COUNT(*) FROM albums_2026 WHERE album_name LIKE '%遊%' OR album_name LIKE '%戲%'")
cnt2 = c.fetchone()[0]
lines.append(f'  album_name 含繁体: {cnt2} 条')
# 检查 cover_image_url 字段
c.execute("SELECT COUNT(*) FROM albums_2026 WHERE cover_image_url LIKE '%張懸%'")
cnt3 = c.fetchone()[0]
lines.append(f'  cover_image_url 含繁体: {cnt3} 条')
lines.append('')

conn.close()

# 检查封面文件是否有繁体残留
covers_dir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\covers'
lines.append(f'=== 检查封面文件繁体残留 ({covers_dir}) ===')
if os.path.exists(covers_dir):
    files = os.listdir(covers_dir)
    fan_files = [f for f in files if '張' in f or '懸' in f or '遊' in f or '戲' in f]
    if fan_files:
        lines.append(f'  Warning: 有 {len(fan_files)} 个繁体文件:')
        for f in fan_files:
            fpath = os.path.join(covers_dir, f)
            size = os.path.getsize(fpath)
            lines.append(f'    {f} ({size} bytes)')
    else:
        lines.append('  OK: 无繁体残留')
else:
    lines.append(f'  目录不存在: {covers_dir}')

output = '\n'.join(lines)

with open(r'C:\Users\qujt\.qclaw\workspace\zx_verify.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print('Done, saved to zx_verify.txt')
