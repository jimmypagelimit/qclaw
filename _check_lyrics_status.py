import sqlite3

db_path = 'C:/Users/qujt/.qclaw/workspace/_music_latest.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 总曲目数
cursor.execute('SELECT COUNT(*) FROM tracks')
total = cursor.fetchone()[0]

# 有歌词的曲目数（text 或 lrc）
cursor.execute("""SELECT COUNT(*) FROM tracks 
              WHERE lyrics_text_path IS NOT NULL AND lyrics_text_path != ''
                 OR lyrics_lrc_path IS NOT NULL AND lyrics_lrc_path != ''""")
have = cursor.fetchone()[0]

# 缺失歌词的曲目数
missing = total - have

# 覆盖率
coverage = have / total * 100 if total > 0 else 0

print(f'Total tracks: {total}')
print(f'Has lyrics: {have}')
print(f'Missing lyrics: {missing}')
print(f'Coverage: {coverage:.1f}%')

# 查看缺失歌词的曲目（前10条）
cursor.execute("""SELECT t.id, t.track_name, a.album_name 
              FROM tracks t 
              LEFT JOIN albums a ON t.album_id = a.album_id
              WHERE (t.lyrics_text_path IS NULL OR t.lyrics_text_path = '') 
                AND (t.lyrics_lrc_path IS NULL OR t.lyrics_lrc_path = '')
              LIMIT 10""")
print('\nSample missing tracks:')
for row in cursor.fetchall():
    print(f'  - {row[1]} (from {row[2]})')

conn.close()
