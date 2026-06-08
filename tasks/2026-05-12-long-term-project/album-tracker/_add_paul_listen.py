import sqlite3

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# 补一条 2026 年 listen_history 记录
cur.execute("INSERT INTO listen_history (album_id, listen_year, listen_date) VALUES (540, 2026, '2026-06-08')")
conn.commit()

# 更新 albums 表 total_listen_count
cur.execute("UPDATE albums SET total_listen_count = total_listen_count + 1 WHERE album_id = 540")
# 设置 first_listen_date
cur.execute("UPDATE albums SET first_listen_date = '2026-06-08' WHERE album_id = 540 AND first_listen_date IS NULL")
conn.commit()

# 验证
cur.execute("SELECT album_name, artist, total_listen_count, first_listen_date FROM albums WHERE album_id = 540")
print(cur.fetchone())
cur.execute("SELECT * FROM listen_history WHERE album_id = 540")
print(cur.fetchone())
conn.close()
print('Done')
