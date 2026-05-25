#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3, os

db = r'G:\原创计划\music'
if os.path.isdir(db):
    db = os.path.join(db, 'music')

conn = sqlite3.connect(db)
c = conn.cursor()

print('=== 验证最终状态 ===')
print()
print('albums 总表:')
c.execute("SELECT album_id, album_name, artist, total_listen_count, overall_score FROM albums WHERE artist LIKE '%张悬%' ORDER BY album_id")
for r in c.fetchall():
    print(r)

print()
print('albums_2026:')
c.execute("SELECT album_id, album_name, artist, total_listen_count, overall_score FROM albums_2026 WHERE artist LIKE '%张悬%' ORDER BY album_id")
for r in c.fetchall():
    print(r)

# 检查是否还有繁体残留
print()
c.execute("SELECT COUNT(*) FROM albums WHERE artist LIKE '%張懸%' OR album_name LIKE '%遊戲%'")
print('albums 繁体残留:', c.fetchone()[0])

c.execute("SELECT COUNT(*) FROM albums_2026 WHERE artist LIKE '%張懸%' OR album_name LIKE '%遊戲%'")
print('albums_2026 繁体残留:', c.fetchone()[0])

conn.close()
print()
print('Done')
