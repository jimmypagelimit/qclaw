#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3, os

db = r'G:\原创计划\music'
if os.path.isdir(db):
    db = os.path.join(db, 'music')

conn = sqlite3.connect(db)
c = conn.cursor()

lines = []
lines.append('=== 验证最终状态 ===')
lines.append('')

lines.append('albums 总表:')
c.execute("SELECT album_id, album_name, artist, total_listen_count, overall_score FROM albums WHERE artist LIKE '%张悬%' ORDER BY album_id")
for r in c.fetchall():
    lines.append(str(r))

lines.append('')
lines.append('albums_2026:')
c.execute("SELECT album_id, album_name, artist, total_listen_count, overall_score FROM albums_2026 WHERE artist LIKE '%张悬%' ORDER BY album_id")
for r in c.fetchall():
    lines.append(str(r))

lines.append('')
c.execute("SELECT COUNT(*) FROM albums WHERE artist LIKE '%張懸%' OR album_name LIKE '%遊戲%'")
lines.append('albums 繁体残留: ' + str(c.fetchone()[0]))

c.execute("SELECT COUNT(*) FROM albums_2026 WHERE artist LIKE '%張懸%' OR album_name LIKE '%遊戲%'")
lines.append('albums_2026 繁体残留: ' + str(c.fetchone()[0]))

conn.close()

output = '\n'.join(lines)
print(output)

# 同时写 UTF-8 文件
with open(r'C:\Users\qujt\.qclaw\workspace\verify_final_utf8.txt', 'w', encoding='utf-8') as f:
    f.write(output)

print('\nDone, saved to verify_final_utf8.txt')
