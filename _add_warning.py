import sqlite3, os, urllib.request, json

# 1. 停 Web 服务
os.system("taskkill /f /im node.exe >nul 2>&1")

# 2. 连接数据库
db = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
db.execute("PRAGMA journal_mode=WAL")
db.execute("BEGIN")

# 3. 添加 artist
cur = db.execute("SELECT artist_id FROM artists WHERE name = ?", ("Warning",))
row = cur.fetchone()
if row:
    artist_id = row[0]
    print(f"Artist exists: ID={artist_id}")
else:
    db.execute("INSERT INTO artists (name, country) VALUES (?,?)", ("Warning", "UK"))
    artist_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    print(f"Added artist: Warning (ID={artist_id})")

# 4. 添加专辑
cur = db.execute("SELECT album_id FROM albums WHERE album_name = ? AND artist = ?", ("Rituals of Shame", "Warning"))
if cur.fetchone():
    print("Album already exists!")
else:
    db.execute("""INSERT INTO albums (album_name, artist, release_year, description, status)
                  VALUES (?,?,?,?,?)""",
              ("Rituals of Shame", "Warning", 2026,
               "UK doom metal. Relapse Records. 5 tracks: Rituals of Shame, Stations, Night Comes Down, Landing Lights, Teacher. "
               "20-year follow-up to the classic Watching from a Distance (2006). Recorded at The Arch Studio (former church in Southport).",
               "active"))
    album_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    print(f"Added album: Rituals of Shame (ID={album_id})")

    # 收听记录 +1
    db.execute("""INSERT INTO listen_history (album_id, listen_date, listen_year, notes)
                  VALUES (?,?,?,?)""",
              (album_id, "2026-06-22", 2026, ""))
    print(f"  +1 listen (2026-06-22)")

db.commit()

# 5. 导出 SQL
with open(r'C:\Users\qujt\.qclaw\workspace\_music_latest.sql', 'w', encoding='utf-8') as f:
    for line in db.iterdump():
        f.write(line + '\n')
print("SQL exported")

db.close()

# 6. 重启 Web 服务
import subprocess
workdir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker'
subprocess.Popen(['node', 'dist/server.js'], cwd=workdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print("Web service restarted")
print("Done!")
