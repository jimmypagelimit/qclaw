import sqlite3, datetime

db = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"
conn = sqlite3.connect(db)
c = conn.cursor()

# Find album_id
c.execute("SELECT album_id, album_name, artist FROM albums WHERE artist LIKE '%Car Seat Headrest%' AND album_name LIKE '%Denial%'")
row = c.fetchone()
if not row:
    print("Album not found")
else:
    album_id = row[0]
    print(f"Found: {row}")

    today = datetime.date.today()
    listen_date = today.strftime("%Y-%m-%d")
    year = today.year

    c.execute("SELECT COUNT(*) FROM listen_history WHERE album_id=? AND listen_year=?", (album_id, year))
    before = c.fetchone()[0]
    print(f"Before: {before} listens in {year}")

    c.execute("INSERT INTO listen_history (album_id, listen_date, listen_year) VALUES (?, ?, ?)",
              (album_id, listen_date, year))
    conn.commit()

    c.execute("SELECT COUNT(*) FROM listen_history WHERE album_id=? AND listen_year=?", (album_id, year))
    after = c.fetchone()[0]
    print(f"After: {after} listens in {year}")

conn.close()
