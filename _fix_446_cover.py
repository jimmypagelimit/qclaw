import sqlite3
conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()
cur.execute('UPDATE albums SET cover_image_url=? WHERE album_id=?', ('/covers/446-海朋森-我不要别的历史.jpg', 446))
conn.commit()
print('Updated cover_image_url for album 446')
conn.close()