import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')

# 找出缺歌词的中文专辑（按曲目数降序）
cur = conn.cursor()
cur.execute('''
    SELECT a.album_id, a.artist, a.album_name,
           (SELECT COUNT(*) FROM tracks t2
            WHERE t2.album_id=a.album_id
            AND t2.lyrics_lrc_path IS NULL AND t2.lyrics_text_path IS NULL) as missing
    FROM albums a
    WHERE missing > 0
    AND (a.country IN ('中国','台湾','香港') OR a.country = 'TW' OR a.country = 'CN')
    ORDER BY missing DESC
    LIMIT 15
''')
rows = cur.fetchall()
print('中文专辑缺歌词TOP:')
for r in rows:
    print('  [%s] %s - %s (缺%s首)' % (r[0], r[1], r[2], r[3]))

conn.close()
