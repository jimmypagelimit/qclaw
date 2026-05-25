#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3, os

db = r'G:\原创计划\music'
if os.path.isdir(db):
    db = os.path.join(db, 'music')

conn = sqlite3.connect(db)
c = conn.cursor()

print('=== 修复 albums_2026 专辑名（繁→简）===')
c.execute("SELECT album_id, album_name, artist FROM albums_2026 WHERE artist LIKE '%张悬%'")
before = c.fetchall()
print('BEFORE:', before)

# 更新专辑名
c.execute("UPDATE albums_2026 SET album_name='城市' WHERE album_name='城市' AND artist LIKE '%张悬%'")
print('城市: updated', c.rowcount)

c.execute("UPDATE albums_2026 SET album_name='神的游戏' WHERE album_name LIKE '%神的遊戲%'")
print('神的游戏: updated', c.rowcount)

c.execute("SELECT album_id, album_name, artist FROM albums_2026 WHERE artist LIKE '%张悬%'")
after = c.fetchall()
print('AFTER:', after)

conn.commit()
conn.close()
print('Done')
