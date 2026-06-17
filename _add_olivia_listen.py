import sqlite3
from datetime import date

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()

# 查 Olivia 专辑
c.execute("SELECT id, album_name, artist FROM albums WHERE artist LIKE '%Olivia%' OR album_name LIKE '%Olivia%'")
rows = c.fetchall()
print('Olivia albums:', rows)

# album_id=555 是 Olivia 新专辑
album_id = 555
today = date.today().isoformat()

# 查已有记录数
c.execute("SELECT COUNT(*) FROM listen_history WHERE album_id=?", (album_id,))
count = c.fetchone()[0]
print(f'Existing listen_history records for album_id={album_id}: {count}')

# 加一条今天的记录
c.execute("INSERT INTO listen_history (album_id, listen_date) VALUES (?, ?)", (album_id, today))
conn.commit()
print(f'Inserted new listen_history record for album_id={album_id} on {today}')

# 验证
c.execute("SELECT COUNT(*) FROM listen_history WHERE album_id=?", (album_id,))
new_count = c.fetchone()[0]
print(f'Total listen_history records now: {new_count}')

conn.close()
