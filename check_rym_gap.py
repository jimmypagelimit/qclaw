#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查 RYM 评分覆盖情况"""

import sqlite3
import re

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# 总专辑数
cur.execute('SELECT COUNT(*) FROM albums')
total = cur.fetchone()[0]

# 有 RYM 评分的
cur.execute('SELECT COUNT(*) FROM albums WHERE rym_rating IS NOT NULL')
with_rym = cur.fetchone()[0]

# 无 RYM 评分的
cur.execute('SELECT COUNT(*) FROM albums WHERE rym_rating IS NULL')
without_rym = cur.fetchone()[0]

print(f'Total albums: {total}')
print(f'With RYM rating: {with_rym} ({with_rym*100/total:.1f}%)')
print(f'Without RYM rating: {without_rym} ({without_rym*100/total:.1f}%)')

# 前10张无评分的英文专辑（优先回填）
cur.execute('SELECT album_id, album_name, artist FROM albums WHERE rym_rating IS NULL ORDER BY album_id LIMIT 20')
rows = cur.fetchall()
# 过滤中文艺人
non_chinese = [r for r in rows if not re.search(r'[\u4e00-\u9fa5]', r[2])]
print('\nFirst 10 non-Chinese albums without RYM rating:')
for row in non_chinese[:10]:
    print(f'  {row[0]}: {row[1]} - {row[2]}')

conn.close()
