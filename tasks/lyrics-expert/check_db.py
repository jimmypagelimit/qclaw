"""
检查音乐数据库结构
"""
import sqlite3

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'

conn = sqlite3.connect(DB)
cur = conn.cursor()

# 获取所有表
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
print('数据库表:', [t[0] for t in tables])

# 检查albums表结构
cur.execute("PRAGMA table_info(albums)")
columns = cur.fetchall()
print('\nalbums表结构:')
for col in columns:
    print(f'  {col[1]} ({col[2]})')

# 检查是否有tracks表
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%track%'")
track_tables = cur.fetchall()
print(f'\n可能的曲目表: {[t[0] for t in track_tables]}')

# 采样几张专辑
cur.execute("SELECT album_id, artist, album_name FROM albums LIMIT 5")
samples = cur.fetchall()
print('\n采样专辑:')
for album_id, artist, album in samples:
    print(f'  {album_id}: {artist} - {album}')

conn.close()
