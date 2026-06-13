import sqlite3
c = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
r = c.execute("SELECT COUNT(*) FROM albums WHERE cover_image_url IS NULL OR cover_image_url = ''")
print('remaining:', r.fetchone()[0])
c.close()