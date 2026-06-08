import sqlite3
conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()

# 插入 3 条 2026 年收听记录
records = [
    (323, '2026-01-15', 2026),
    (323, '2026-03-15', 2026),
    (323, '2026-06-01', 2026),
]
for album_id, listen_date, listen_year in records:
    cur.execute(
        "INSERT INTO listen_history (album_id, listen_date, listen_year) VALUES (?, ?, ?)",
        (album_id, listen_date, listen_year)
    )
    print(f"Inserted: album_id={album_id}, date={listen_date}")

# 更新 total_listen_count
cur.execute("UPDATE albums SET total_listen_count = total_listen_count + 3 WHERE album_id = 323")
cur.execute("SELECT total_listen_count FROM albums WHERE album_id = 323")
new_total = cur.fetchone()[0]
print(f"\nTwin Fantasy total_listen_count updated to: {new_total}")

conn.commit()
conn.close()
print("\nDone.")
