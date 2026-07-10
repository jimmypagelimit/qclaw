import sqlite3, datetime

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()

# 宋冬野《再想想》(ID=600)
album_id = 600

# 查看当前听歌次数
cur.execute('SELECT COUNT(*) FROM listen_history WHERE album_id=?', (album_id,))
current = cur.fetchone()[0]
print(f'当前听歌次数: {current}')

# 新增1条听歌记录（今天）
today = datetime.date.today().isoformat()
cur.execute('INSERT INTO listen_history (album_id, listen_date, listen_year) VALUES (?, ?, ?)',
            (album_id, today, 2026))
conn.commit()

# 验证
cur.execute('SELECT COUNT(*) FROM listen_history WHERE album_id=?', (album_id,))
new_count = cur.fetchone()[0]
print(f'新增后听歌次数: {new_count}')

conn.close()
print('完成！')
