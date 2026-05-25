#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并张悬繁体专辑到简体，并去重
"""
import sqlite3, os

db = r'G:\原创计划\music'
if os.path.isdir(db):
    db = os.path.join(db, 'music')

conn = sqlite3.connect(db)
c = conn.cursor()

# 1. 查所有张悬相关专辑（albums 总表）
print('=== BEFORE: albums 总表 ===')
c.execute("SELECT album_id, album_name, artist, total_listen_count, overall_score, first_listen_date FROM albums WHERE artist LIKE '%张悬%' OR artist LIKE '%張懸%' OR artist LIKE '%Deserts%' ORDER BY album_name, artist")
before = c.fetchall()
for r in before:
    print(r)

# 按 (album_name, artist_simplified) 分组，找重复
# 448=亲爱的(繁), 449=不一样的游戏(繁)
# 检查 2026 年份表
print('\n=== BEFORE: albums_2026 ===')
c.execute("SELECT album_id, album_name, artist, total_listen_count, overall_score FROM albums_2026 WHERE artist LIKE '%张悬%' OR artist LIKE '%張懸%' OR artist LIKE '%Deserts%' ORDER BY album_name")
before_2026 = c.fetchall()
for r in before_2026:
    print(r)

# 合并逻辑：
# 1. album_id 448 "亲爱的" artist "張懸 [Deserts Chang]" → 更新为 "张悬 [Deserts Chang]"
# 2. album_id 449 "不一样的游戏 [Games We Play]" artist "張懸 [Deserts Chang]" → 更新为 "张悬 [Deserts Chang]"
# 3. 检查是否有简体版重复，有则合并 listen_count

# 先查简体版是否已存在
print('\n=== 检查简体版是否已存在 ===')
c.execute("SELECT album_id, album_name, artist, total_listen_count, overall_score FROM albums WHERE artist LIKE '张悬%'")
sx = c.fetchall()
print('简体版:', sx)

if not sx:
    # 没有简体版，直接把繁体版 artist 字段更新为简体
    print('\n→ 无简体版，直接更新 artist 为简体...')
    c.execute("UPDATE albums SET artist='张悬 [Deserts Chang]' WHERE artist='張懸 [Deserts Chang]'")
    c.execute("UPDATE albums_2026 SET artist='张悬 [Deserts Chang]' WHERE artist='張懸 [Deserts Chang]'")
    conn.commit()
    print('已更新 artist: 張懸 → 张悬')
else:
    # 有简体版，需要合并
    print('\n→ 发现简体版，执行合并...')
    # 合并逻辑：把繁体版的 listen_count 加到简体版，删繁体版
    pass  # TODO

# 再看 after
print('\n=== AFTER: albums 总表 ===')
c.execute("SELECT album_id, album_name, artist, total_listen_count, overall_score FROM albums WHERE artist LIKE '%张悬%' OR artist LIKE '%Deserts%' ORDER BY album_name")
after = c.fetchall()
for r in after:
    print(r)

print('\n=== AFTER: albums_2026 ===')
c.execute("SELECT album_id, album_name, artist, total_listen_count, overall_score FROM albums_2026 WHERE artist LIKE '%张悬%' OR artist LIKE '%Deserts%' ORDER BY album_name")
after_2026 = c.fetchall()
for r in after_2026:
    print(r)

conn.close()
print('\nDone')
