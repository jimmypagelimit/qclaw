import sqlite3, shutil
db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
local = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\_music_latest.db'
shutil.copy2(db, local)
conn = sqlite3.connect(local)
cur = conn.cursor()
cur.execute("UPDATE albums SET cover_image_url='/covers/71-大只佬-V是兔子.jpg' WHERE album_id=71")
print(f"Rows updated: {cur.rowcount}")
conn.commit()
# verify
cur.execute("SELECT album_id, album_name, artist, cover_image_url FROM albums WHERE album_id=71")
print(cur.fetchone())
conn.close()
