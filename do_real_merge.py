#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真正合并张悬繁体重复专辑到简体版
albums 总表里简体版已存在，繁体版(id=448,449)是重复，需合并tc后删除
"""
import sqlite3, os, sys

db = r'G:\原创计划\music'
if os.path.isdir(db):
    db = os.path.join(db, 'music')

sys.stdout = open(r'C:\Users\qujt\.qclaw\workspace\merge_final_report.txt', 'w', encoding='utf-8')
sys.stderr = sys.stdout

print('=== 张悬专辑真正合并（繁体→简体）===')
print('DB:', db)
print()

conn = sqlite3.connect(db)
c = conn.cursor()

# 合并映射：
# id=448 "城市" (tc=1) → 合并到 id=168 "城市" (tc=4)
# id=449 "神的遊戲 Games We Play" (tc=1) → 合并到 id=6 "神的游戏" (tc=4)
# 同时更新专辑名为简体

print('=== BEFORE ===')
c.execute("SELECT album_id, album_name, artist, total_listen_count, overall_score FROM albums WHERE album_id IN (6,168,448,449)")
for r in c.fetchall():
    print(r)

print()
print('=== 开始合并 ===')

# 1. 合并 id=448 → id=168
c.execute("SELECT total_listen_count, overall_score FROM albums WHERE album_id=?", (448,))
row448 = c.fetchone()
tc448 = row448[0] or 0
score448 = row448[1]

c.execute("SELECT total_listen_count, overall_score FROM albums WHERE album_id=?", (168,))
row168 = c.fetchone()
tc168 = row168[0] or 0
score168 = row168[1]

new_tc_168 = tc168 + tc448
new_score_168 = max(score168 or 0, score448 or 0) or None

c.execute("UPDATE albums SET total_listen_count=?, overall_score=?, artist=? WHERE album_id=?", 
          (new_tc_168, new_score_168, '张悬', 168))
print(f'合并 448→168: tc {tc448}+{tc168}={new_tc_168}, score={new_score_168}')
print(f'  删除 id=448')

# 2. 合并 id=449 → id=6
c.execute("SELECT total_listen_count, overall_score FROM albums WHERE album_id=?", (449,))
row449 = c.fetchone()
tc449 = row449[0] or 0
score449 = row449[1]

c.execute("SELECT total_listen_count, overall_score FROM albums WHERE album_id=?", (6,))
row6 = c.fetchone()
tc6 = row6[0] or 0
score6 = row6[1]

new_tc_6 = tc6 + tc449
new_score_6 = max(score6 or 0, score449 or 0) or None

c.execute("UPDATE albums SET total_listen_count=?, overall_score=?, artist=? WHERE album_id=?", 
          (new_tc_6, new_score_6, '张悬', 6))
print(f'合并 449→6: tc {tc449}+{tc6}={new_tc_6}, score={new_score_6}')
print(f'  删除 id=449')

# 3. 删除繁体重复条目
c.execute("DELETE FROM albums WHERE album_id IN (448, 449)")
print('已删除 albums 中 id=448, 449')

# 4. 更新专辑名为简体（albums 总表）
c.execute("UPDATE albums SET album_name='神的游戏' WHERE album_id=6 AND album_name LIKE '%神的遊戲%'")
print('albums: id=6 专辑名确认简体: 神的游戏')

# 5. albums_2026 表：直接改 artist + 专辑名（无简体版重复，无需删除）
c.execute("SELECT album_id, album_name, artist FROM albums_2026 WHERE artist LIKE '%張懸%'")
rows2026 = c.fetchall()
print()
print('=== albums_2026 处理 ===')
for r in rows2026:
    id2026, name2026, art2026 = r
    new_name = name2026.replace('遊戲', '游戏')
    c.execute("UPDATE albums_2026 SET artist=?, album_name=? WHERE album_id=?", 
              ('张悬 [Deserts Chang]', new_name, id2026))
    print(f'  id={id2026}: artist {art2026} → 张悬 [Deserts Chang], album {name2026} → {new_name}')

conn.commit()

print()
print('=== AFTER ===')
c.execute("SELECT album_id, album_name, artist, total_listen_count, overall_score FROM albums WHERE artist LIKE '%张悬%' ORDER BY album_id")
for r in c.fetchall():
    print(r)

print()
c.execute("SELECT album_id, album_name, artist, total_listen_count, overall_score FROM albums_2026 WHERE artist LIKE '%张悬%' ORDER BY album_id")
for r in c.fetchall():
    print(r)

print()
c.execute("SELECT COUNT(*) FROM albums WHERE artist LIKE '%張懸%'")
print('残留繁体 artist 条目数:', c.fetchone()[0])

conn.close()
print('\nDone')
