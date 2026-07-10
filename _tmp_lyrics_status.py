import sqlite3, os

db = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
c = db.cursor()

c.execute('SELECT COUNT(*) FROM tracks')
total = c.fetchone()[0]

c.execute("SELECT COUNT(*) FROM tracks WHERE lyrics_text_path IS NOT NULL AND lyrics_text_path != ''")
have_lyrics = c.fetchone()[0]

c.execute("SELECT COUNT(*) FROM tracks WHERE lyrics_text_path IS NULL OR lyrics_text_path = ''")
missing = c.fetchone()[0]

c.execute("SELECT COUNT(*) FROM tracks WHERE lyrics_text_path IS NULL")
null_count = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM tracks WHERE lyrics_text_path = ''")
empty_count = c.fetchone()[0]

c.execute("SELECT COUNT(*) FROM tracks WHERE lyrics_text_path IS NOT NULL AND lyrics_text_path != '' AND lyrics_text_path NOT LIKE '%tasks%' AND lyrics_text_path NOT LIKE '%.txt' AND lyrics_text_path NOT LIKE '%.lrc'")
garbled = c.fetchone()[0]

# Missing lyrics by album with artist
c.execute("""
    SELECT a.artist, a.album_name, COUNT(*) as cnt
    FROM tracks t
    JOIN albums a ON t.album_id = a.album_id
    WHERE t.lyrics_text_path IS NULL OR t.lyrics_text_path = ''
    GROUP BY t.album_id
    ORDER BY cnt DESC
    LIMIT 20
""")
print('缺失歌词最多的专辑/艺人（前20）:')
rows = c.fetchall()
for row in rows:
    artist = row[0] if row[0] else '(null)'
    album = row[1] if row[1] else '(null)'
    print(f'  {repr(artist)} - {repr(album)}: {row[2]}首')

print()

# Check disk lyrics
lyrics_dir = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics'
if os.path.exists(lyrics_dir):
    disk_count = len([f for f in os.listdir(lyrics_dir) if f.endswith('.txt') or f.endswith('.lrc')])
    print(f'磁盘歌词文件数: {disk_count}')
else:
    print(f'磁盘歌词目录不存在')

# Count path-file existence
c.execute("SELECT lyrics_text_path FROM tracks WHERE lyrics_text_path IS NOT NULL AND lyrics_text_path != ''")
total_with_path = 0
count_exist = 0
for row in c.fetchall():
    total_with_path += 1
    if os.path.exists(row[0]):
        count_exist += 1
print(f'有路径的条目: {total_with_path}')
print(f'路径对应文件存在的: {count_exist}')
print(f'路径文件不存在的: {total_with_path - count_exist}')

print(f'\n总tracks: {total}')
print(f'有歌词路径: {have_lyrics}')
print(f'缺失歌词: {missing}')
print(f'  NULL值: {null_count}')
print(f'  空字符串: {empty_count}')
print(f'  GBK乱码疑似: {garbled}')

db.close()
