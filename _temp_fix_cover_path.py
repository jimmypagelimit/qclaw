import sqlite3

conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
c = conn.cursor()

# 更新 554 的封面路径
c.execute("UPDATE albums SET cover_image_url=? WHERE album_id=?", 
          ('/covers/554-Car Seat Headrest-Teens of Style.jpg', 554))
print('554 updated:', c.rowcount)

# 更新 426 的封面路径（先检查正确文件名）
import os
cover_dir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers'
for f in os.listdir(cover_dir):
    if f.startswith('426-'):
        print('426 file:', f)
        c.execute("UPDATE albums SET cover_image_url=? WHERE album_id=?", 
                  (f'/covers/{f}', 426))
        print('426 updated:', c.rowcount)
        break

conn.commit()
conn.close()
