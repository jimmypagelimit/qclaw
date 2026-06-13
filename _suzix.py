import sqlite3, datetime

db = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"
conn = sqlite3.connect(db)
c = conn.cursor()

# 查找
c.execute("SELECT album_id, album_name, artist, total_listen_count FROM albums WHERE artist LIKE '%苏紫旭%' AND album_name LIKE '%悲歌%'")
row = c.fetchone()
if not row:
    print("Album not found")
else:
    album_id, name, artist, total = row
    print(f"Found: {artist} - {name} (id={album_id}, total={total})")

    today = datetime.date.today()
    year = today.year
    listen_date = today.strftime("%Y-%m-%d")

    # 加一条
    c.execute("INSERT INTO listen_history (album_id, listen_date, listen_year) VALUES (?, ?, ?)", (album_id, listen_date, year))

    # 更新 total
    c.execute("UPDATE albums SET total_listen_count = total_listen_count + 1 WHERE album_id = ?", (album_id,))

    conn.commit()

    c.execute("SELECT COUNT(*) FROM listen_history WHERE album_id=? AND listen_year=?", (album_id, year))
    count_2026 = c.fetchone()[0]
    c.execute("SELECT total_listen_count FROM albums WHERE album_id=?", (album_id,))
    total_new = c.fetchone()[0]
    print(f"2026 listens: {count_2026}, total: {total_new}")

conn.close()
