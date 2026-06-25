"""
检查tracks表结构并采样
"""
import sqlite3

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'

conn = sqlite3.connect(DB)
cur = conn.cursor()

# 检查tracks表结构
cur.execute("PRAGMA table_info(tracks)")
columns = cur.fetchall()
with open(r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\tracks_schema.txt', 'w', encoding='utf-8') as f:
    f.write('tracks表结构:\n')
    for col in columns:
        f.write(f'  {col[1]} ({col[2]})\n')

# 采样tracks数据
cur.execute("SELECT * FROM tracks LIMIT 10")
rows = cur.fetchall()
with open(r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\tracks_sample.txt', 'w', encoding='utf-8') as f:
    f.write('tracks采样数据:\n')
    for row in rows:
        f.write(f'  {row}\n')

# 检查tracks和albums的关系
cur.execute("""
    SELECT t.track_id, t.track_name, t.album_id, a.album_name
    FROM tracks t
    JOIN albums a ON t.album_id = a.album_id
    LIMIT 10
""")
relations = cur.fetchall()
with open(r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\tracks_relation.txt', 'w', encoding='utf-8') as f:
    f.write('tracks与albums关系采样:\n')
    for row in relations:
        f.write(f'  track_id={row[0]}, track_name={row[1]}, album_id={row[2]}, album={row[3]}\n')

print('完成，结果已保存到文件')
conn.close()
