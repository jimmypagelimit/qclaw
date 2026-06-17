import sqlite3, shutil
src = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
dst = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\_music_latest.db'
shutil.copy2(src, dst)
conn = sqlite3.connect(dst)
cur = conn.cursor()
cur.execute("SELECT id, album_name, artist, cover_image_url FROM albums WHERE artist LIKE ? OR album_name LIKE ?", ('%大只佬%', '%V%'))
rows = cur.fetchall()
for r in rows:
    print(r)
if not rows:
    cur.execute("SELECT id, album_name, artist, cover_image_url FROM albums WHERE id=123")
    rows = cur.fetchall()
    for r in rows:
        print(r)
conn.close()
