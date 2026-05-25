#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并张悬繁体专辑到简体，汇报前后数据差距
"""
import sqlite3, os, sys

db = r'G:\原创计划\music'
if os.path.isdir(db):
    db = os.path.join(db, 'music')

sys.stdout = open(r'C:\Users\qujt\.qclaw\workspace\merge_report.txt', 'w', encoding='utf-8')
sys.stderr = sys.stdout

print('=== 合并张悬繁体→简体 ===')
print('DB:', db, 'exists:', os.path.exists(db))
print()

conn = sqlite3.connect(db)
c = conn.cursor()

# 所有相关表
tables = ['albums']
for y in [2024, 2025, 2026]:
    t = f'albums_{y}'
    c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{t}'")
    if c.fetchone():
        tables.append(t)

print('检查表:', tables)
print()

# 收集所有张悬相关专辑（繁体+简体+英文名）
# 繁体：張懸  简体：张悬
before = {}  # key = (simplified_album_name, simplified_artist) → list of rows

for tbl in tables:
    try:
        c.execute(f"SELECT album_id, album_name, artist, total_listen_count, overall_score, first_listen_date FROM {tbl} WHERE artist LIKE '%张悬%' OR artist LIKE '%張懸%' OR artist LIKE '%Deserts%'")
        for row in c.fetchall():
            album_id, album_name, artist, tc, score, fld = row
            # 繁体→简体映射
            s_artist = artist.replace('張懸', '张悬')
            s_album = album_name  # 专辑名也可能繁体
            key = (s_album, s_artist, tbl)
            if key not in before:
                before[key] = []
            before[key].append({'id': album_id, 'tbl': tbl, 'artist_raw': artist, 'album_raw': album_name, 'tc': tc, 'score': score, 'fld': fld})
    except Exception as e:
        print(f'Error querying {tbl}:', e)

print('=== BEFORE ===')
total_before = 0
for key, rows in before.items():
    alb, art, tbl = key
    print(f'表={tbl} 专辑={alb} 艺术家={art}')
    for r in rows:
        print(f'  id={r["id"]} artist_raw={r["artist_raw"]} album_raw={r["album_raw"]} tc={r["tc"]} score={r["score"]}')
    total_before += len(rows)
print(f'总条目数: {total_before}')
print()

# 合并逻辑：
# 1. 同一 (s_album, s_artist, tbl) 下如果有多个条目，合并 tc 和 score
# 2. 把 artist 字段从繁体更新为简体

print('=== 合并中 ===')
merge_log = []
for key, rows in before.items():
    alb, art, tbl = key
    if len(rows) == 1:
        # 只有一个条目，直接更新 artist
        r = rows[0]
        if r['artist_raw'] != art:
            c.execute(f"UPDATE {tbl} SET artist=? WHERE album_id=?", (art, r['id']))
            merge_log.append(f'{tbl}.{r["id"]}: artist {r["artist_raw"]} → {art}')
    else:
        # 多个条目，合并到第一个（保留最早 first_listen_date 的那个）
        rows_sorted = sorted(rows, key=lambda x: x['fld'] or '')
        keep = rows_sorted[0]
        merge_ids = [r['id'] for r in rows_sorted[1:]]
        
        # 合并 total_listen_count
        total_tc = sum(r['tc'] or 0 for r in rows)
        # 合并 score（取平均或保留最高的，这里取最高）
        scores = [r['score'] for r in rows if r['score'] is not None]
        new_score = max(scores) if scores else None
        
        c.execute(f"UPDATE {tbl} SET total_listen_count=?, overall_score=?, artist=? WHERE album_id=?", 
                  (total_tc, new_score, art, keep['id']))
        merge_log.append(f'{tbl}: 合并 {merge_ids} → {keep["id"]}, tc={total_tc}, score={new_score}')
        
        # 删除被合并的条目
        for mid in merge_ids:
            c.execute(f"DELETE FROM {tbl} WHERE album_id=?", (mid,))
            merge_log.append(f'{tbl}: 删除重复 id={mid}')

if merge_log:
    print('合并操作:')
    for m in merge_log:
        print(' ', m)
else:
    print('无需合并（无重复或无需更新）')
print()

conn.commit()

# AFTER
print('=== AFTER ===')
after = {}
for tbl in tables:
    try:
        c.execute(f"SELECT album_id, album_name, artist, total_listen_count, overall_score, first_listen_date FROM {tbl} WHERE artist LIKE '%张悬%' OR artist LIKE '%Deserts%'")
        for row in c.fetchall():
            album_id, album_name, artist, tc, score, fld = row
            s_artist = artist.replace('張懸', '张悬')
            s_album = album_name
            key = (s_album, s_artist, tbl)
            if key not in after:
                after[key] = []
            after[key].append({'id': album_id, 'tbl': tbl, 'artist': artist, 'album': album_name, 'tc': tc, 'score': score, 'fld': fld})
    except:
        pass

total_after = 0
for key, rows in after.items():
    alb, art, tbl = key
    print(f'表={tbl} 专辑={alb} 艺术家={art}')
    for r in rows:
        print(f'  id={r["id"]} artist={r["artist"]} album={r["album"]} tc={r["tc"]} score={r["score"]}')
    total_after += len(rows)
print(f'总条目数: {total_after}')
print()

print('=== 差距 ===')
print(f'合并前条目数: {total_before}')
print(f'合并后条目数: {total_after}')
print(f'减少条目数: {total_before - total_after}')

conn.close()
print('\nDone, report saved to merge_report.txt')
