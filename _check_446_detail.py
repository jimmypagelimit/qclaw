import sqlite3
conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()
cur.execute('SELECT album_id, album_name, artist FROM albums WHERE album_id=446')
row = cur.fetchone()
print('DB album_name:', row[1])
print('DB artist:', row[2])

# 修正专辑名
cur.execute('UPDATE albums SET album_name=? WHERE album_id=?', ('我不要别的历史', 446))
conn.commit()
print('Updated album_name to: 我不要别的历史')
conn.close()