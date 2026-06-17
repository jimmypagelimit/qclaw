import sqlite3
conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()
# 更新 album_id=427 的封面路径
cur.execute("UPDATE albums SET cover_image_url = '/covers/427-施鑫文月-巴蜀文艺复兴第二章.jpg' WHERE album_id = 427")
conn.commit()
print(f"Updated: {cur.rowcount} rows")
cur.execute("SELECT album_id, cover_image_url FROM albums WHERE album_id = 427")
print(cur.fetchone())
conn.close()
