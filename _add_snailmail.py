import sqlite3
import os

# 1. 结束 node 进程（Web 服务）
os.system("taskkill /f /im node.exe >nul 2>&1")

# 2. 连接数据库
db = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
db.execute("PRAGMA journal_mode=WAL")
db.execute("BEGIN")

# 3. 检查/添加 artist
cur = db.execute("SELECT artist_id FROM artists WHERE name = ?", ("Snail Mail",))
row = cur.fetchone()
if row:
    artist_id = row[0]
    print(f"Artist already exists: ID={artist_id}")
else:
    db.execute("INSERT INTO artists (name, country) VALUES (?,?)", ("Snail Mail", "US"))
    artist_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    print(f"Added artist: Snail Mail (ID={artist_id})")

# 4. 添加专辑
albums = [
    ("Lush", "Snail Mail", 2018),
    ("Valentine", "Snail Mail", 2021),
]

for album_name, artist, year in albums:
    cur = db.execute("SELECT album_id FROM albums WHERE album_name = ? AND artist = ?", (album_name, artist))
    if cur.fetchone():
        print(f"Album already exists: {album_name}")
        continue
    
    db.execute("""INSERT INTO albums 
                  (album_name, artist, release_year, description, status)
                  VALUES (?,?,?,?,?)""",
              (album_name, artist, year, "", "active"))
    album_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    print(f"Added album: {album_name} (ID={album_id})")
    
    # 添加收听记录（1次，今天）
    db.execute("""INSERT INTO listen_history 
                  (album_id, listen_date, listen_year, notes)
                  VALUES (?,?,?,?)""",
              (album_id, "2026-06-21", 2026, ""))
    print(f"  +1 listen (2026-06-21)")

db.commit()
db.close()
print("Done!")
