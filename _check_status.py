#!/usr/bin/env python3
"""检查L项目和最近入库专辑"""
import sqlite3, os, datetime

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
LYRICS_DIR = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics'

print('=== L项目状态 ===')
if os.path.exists(LYRICS_DIR):
    lrc_count = txt_count = 0
    for root, dirs, files in os.walk(LYRICS_DIR):
        for f in files:
            if f.endswith('.lrc'): lrc_count += 1
            elif f.endswith('.txt'): txt_count += 1
    print(f'歌词文件: LRC={lrc_count}, TXT={txt_count}')

conn = sqlite3.connect(DB)
cur = conn.cursor()

# tracks表歌词覆盖率
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tracks'")
if cur.fetchone():
    cur.execute('SELECT COUNT(*) FROM tracks')
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM tracks WHERE lyrics_text_path IS NOT NULL AND lyrics_text_path != ''")
    with_lyrics = cur.fetchone()[0]
    pct = with_lyrics*100//total if total else 0
    print(f'数据库覆盖率: {with_lyrics}/{total} ({pct}%)')

# 最近入库专辑（最近入库的10张）
print('\n=== 最近入库专辑（按ID倒序）===')
cur.execute('''
SELECT album_id, album_name, artist, release_year, release_company, cover_image_url, description, genre
FROM albums ORDER BY album_id DESC LIMIT 10
''')
for row in cur.fetchall():
    album_id, name, artist, year, company, cover, desc, genre = row
    missing = []
    if not company: missing.append('发行公司')
    if not cover: missing.append('封面')
    if not desc: missing.append('描述')
    if not genre: missing.append('流派')
    print(f'ID={album_id}: {artist} - {name}')
    print(f'  年份:{year} | 发行:{company or "??"} | 流派:{genre or "??"}')
    print(f'  封面: {"OK" if cover else "MISSING"} | 描述: {"OK" if desc else "MISSING"}')
    if missing: print(f'  缺失: {missing}')
    print()

conn.close()
