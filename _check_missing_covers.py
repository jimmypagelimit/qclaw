import sqlite3
conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM albums WHERE cover_image_url IS NULL OR cover_image_url = '' OR cover_image_url = '/covers/'")
print('missing:', cur.fetchone()[0])
cur.execute("SELECT album_id, album_name, artist, cover_image_url FROM albums WHERE cover_image_url IS NULL OR cover_image_url = '' OR cover_image_url = '/covers/' ORDER BY total_listen_count DESC LIMIT 20")
for r in cur.fetchall():
    print(r)
conn.close()
