import sqlite3, datetime

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()

# 碎梦飞跃《外面是夏天》(ID=599)
album_id = 599

# 检查当前听歌次数
cur.execute('SELECT COUNT(*) FROM listen_history WHERE album_id=?', (album_id,))
current = cur.fetchone()[0]
print(f'当前听歌次数: {current}')

# 新增12条听歌记录（2026年）
today = datetime.date.today().isoformat()
for i in range(12):
    # 分散在2026年的不同日期
    date = f'2026-{((i//3)+1):02d}-{(i%30)+1:02d}'
    try:
        cur.execute('INSERT INTO listen_history (album_id, listen_date, listen_year) VALUES (?, ?, ?)',
                    (album_id, date, 2026))
    except:
        pass  # 跳过重复日期

conn.commit()

# 验证
cur.execute('SELECT COUNT(*) FROM listen_history WHERE album_id=?', (album_id,))
new_count = cur.fetchone()[0]
print(f'新增后听歌次数: {new_count}')

conn.close()
print('完成！')
