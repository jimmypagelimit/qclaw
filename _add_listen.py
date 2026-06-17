import sqlite3
from datetime import date

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()

album_id = 555
today = date.today().isoformat()  # "2026-06-16"
listen_year = date.today().year  # 2026

# 查已有记录数
c.execute("SELECT COUNT(*) FROM listen_history WHERE album_id=?", (album_id,))
count = c.fetchone()[0]
print(f'album_id={album_id} 已有 {count} 条 listen_history 记录')

# 插入新记录
c.execute(
    "INSERT INTO listen_history (album_id, listen_date, listen_year) VALUES (?, ?, ?)",
    (album_id, today, listen_year)
)
conn.commit()

# 验证
c.execute("SELECT COUNT(*) FROM listen_history WHERE album_id=?", (album_id,))
new_count = c.fetchone()[0]
print(f'插入后共有 {new_count} 条记录')

# 查 albums 表确认专辑信息
c.execute("SELECT album_name, artist FROM albums WHERE album_id=?", (album_id,))
album = c.fetchone()
print(f'专辑: {album[0]} - {album[1]}')

conn.close()
print('完成')
