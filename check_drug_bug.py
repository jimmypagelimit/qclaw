#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查 drug bug - Hell for a Basement"""
import sqlite3

db_path = r'G:\原创计划\music'
print('=== 检查 drug bug - Hell for a Basement ===')
print()

conn = sqlite3.connect(db_path)
c = conn.cursor()

# 1. albums 总表检查
print('1. albums 总表检查...')
c.execute("SELECT album_id, album_name, artist, total_listen_count, rating FROM albums WHERE artist LIKE '%drug bug%'")
results = c.fetchall()
if results:
    print(f'  找到 {len(results)} 条记录:')
    for r in results:
        print(f'    id={r[0]}, name={r[1]}, artist={r[2]}, tc={r[3]}, RYM={r[4]}')
else:
    print('  未找到 drug bug')

# 精确匹配
c.execute("SELECT album_id, album_name, artist, total_listen_count, rating FROM albums WHERE album_name = 'Hell for a Basement' AND artist LIKE '%drug bug%'")
exact = c.fetchone()
if exact:
    print(f'  精确匹配: id={exact[0]}, name={exact[1]}, artist={exact[2]}, tc={exact[3]}, RYM={exact[4]}')
else:
    print('  albums 总表未找到精确匹配: drug bug - Hell for a Basement')

print()

# 2. albums_2026 表检查
print('2. albums_2026 表检查...')
c.execute("SELECT album_id, album_name, artist, total_listen_count, rating FROM albums_2026 WHERE artist LIKE '%drug bug%'")
results_2026 = c.fetchall()
if results_2026:
    print(f'  找到 {len(results_2026)} 条记录:')
    for r in results_2026:
        print(f'    id={r[0]}, name={r[1]}, artist={r[2]}, tc={r[3]}, RYM={r[4]}')
else:
    print('  未找到 drug bug')

# 精确匹配
c.execute("SELECT album_id, album_name, artist, total_listen_count, rating FROM albums_2026 WHERE album_name = 'Hell for a Basement' AND artist LIKE '%drug bug%'")
exact_2026 = c.fetchone()
if exact_2026:
    print(f'  精确匹配: id={exact_2026[0]}, name={exact_2026[1]}, artist={exact_2026[2]}, tc={exact_2026[3]}, RYM={exact_2026[4]}')
else:
    print('  albums_2026 表未找到精确匹配: drug bug - Hell for a Basement')

print()
conn.close()
print('=== 检查完成 ===')
