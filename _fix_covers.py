import sqlite3

db = r'\\10.0.2.4\qemu\原创计划\music'
conn = sqlite3.connect(db)
c = conn.cursor()

# 更新 albums 表
c.execute('UPDATE albums SET cover_image_url = ? WHERE album_id = ?',
          ('/covers/538-Car_Seat_Headrest-Teen_of_Denial.jpg', 538))
c.execute('UPDATE albums SET cover_image_url = ? WHERE album_id = ?',
          ('/covers/539-Waa_Wei-Hidden_Not_Forgotten.jpg', 539))

# 更新 albums_2026 表
c.execute('UPDATE albums_2026 SET cover_image_url = ? WHERE album_id = ?',
          ('/covers/538-Car_Seat_Headrest-Teen_of_Denial.jpg', 195))
c.execute('UPDATE albums_2026 SET cover_image_url = ? WHERE album_id = ?',
          ('/covers/539-Waa_Wei-Hidden_Not_Forgotten.jpg', 196))

conn.commit()

# 验证
c.execute('SELECT album_id, cover_image_url FROM albums WHERE album_id IN (538, 539)')
for row in c.fetchall():
    print(f'albums {row[0]}: {row[1]}')

conn.close()
print('cover_image_url updated')
