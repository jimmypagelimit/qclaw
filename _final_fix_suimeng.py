import sqlite3, datetime

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()

album_id = 599

# 先删除所有现有记录
cur.execute('DELETE FROM listen_history WHERE album_id=?', (album_id,))
print('已删除所有旧记录')

# 插入2条记录（用户要求总共2次）
dates = ['2026-01-01', '2026-07-04']
for d in dates:
    cur.execute('INSERT INTO listen_history (album_id, listen_date, listen_year) VALUES (?, ?, ?)',
                (album_id, d, 2026))

conn.commit()

# 验证
cur.execute('SELECT COUNT(*) FROM listen_history WHERE album_id=?', (album_id,))
count = cur.fetchone()[0]
print(f'碎梦飞跃《外面是夏天》听歌次数已修正为: {count}次')

conn.close()

# 导出SQL
import subprocess
subprocess.run([r'C:\Python311\python.exe', 
                r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\scripts\export_sql.py'])
print('✅ 已导出 database.sql')
