import sqlite3
db = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute("SELECT album_id, album_name, artist, total_listen_count FROM albums WHERE album_id = 382")
row = c.fetchone()
print(f"albums.total_listen_count: {row[3]}")
c.execute("SELECT COUNT(*) FROM listen_history WHERE album_id = 382")
print(f"listen_history rows: {c.fetchone()[0]}")
conn.close()