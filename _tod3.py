import sqlite3
db = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"
conn = sqlite3.connect(db)
c = conn.cursor()

c.execute("SELECT album_id, album_name, artist, total_listen_count FROM albums WHERE album_id = 382")
row = c.fetchone()
print(f"Before: total_listen_count={row[3]}")

c.execute("UPDATE albums SET total_listen_count = (SELECT COUNT(*) FROM listen_history WHERE listen_history.album_id = albums.album_id) WHERE album_id = 382")
conn.commit()

c.execute("SELECT album_id, total_listen_count FROM albums WHERE album_id = 382")
print(f"After:  total_listen_count={c.fetchone()[1]}")
conn.close()