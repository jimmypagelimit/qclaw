import sqlite3

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()

# 碎梦飞跃《外面是夏天》(ID=599)
album_id = 599

# 查看所有听歌记录
cur.execute('''SELECT l.id, l.listen_date, l.listen_year 
              FROM listen_history l 
              WHERE l.album_id=? 
              ORDER BY l.listen_date''', (album_id,))
records = cur.fetchall()

print(f'碎梦飞跃《外面是夏天》(ID={album_id}) 的听歌记录：')
print(f'总次数: {len(records)}\n')

if records:
    for r in records:
        print(f'  ID={r[0]}, 日期={r[1]}, 年份={r[2]}')
else:
    print('  (无记录)')

# 检查专辑是否存在
cur.execute('SELECT album_name, artist FROM albums WHERE album_id=?', (album_id,))
album = cur.fetchone()
if album:
    print(f'\n专辑信息: {album[1]} - {album[0]}')
else:
    print(f'\n⚠️ 专辑ID={album_id} 不存在！')

conn.close()
