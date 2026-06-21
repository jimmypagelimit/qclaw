import sqlite3
import os

# 1. 结束 node 进程
os.system("taskkill /f /im node.exe >nul 2>&1")

# 2. 连接数据库
db = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
db.execute("PRAGMA journal_mode=WAL")
db.execute("BEGIN")

# 3. 删除收听记录
album_ids = [594, 595]
for aid in album_ids:
    db.execute("DELETE FROM listen_history WHERE album_id = ?", (aid,))
    print(f"Deleted listen_history for album_id={aid}")

# 4. 删除专辑
for aid in album_ids:
    db.execute("DELETE FROM albums WHERE album_id = ?", (aid,))
    print(f"Deleted album_id={aid}")

# 5. 检查 artists 表是否需要清理（如果没有其他专辑就删除）
cur = db.execute("SELECT album_id FROM albums WHERE artist = 'Snail Mail' LIMIT 1")
if not cur.fetchone():
    db.execute("DELETE FROM artists WHERE name = 'Snail Mail'")
    print("Deleted artist: Snail Mail (no albums left)")
else:
    print("Artist Snail Mail has other albums, kept")

db.commit()

# 6. 验证
cur = db.execute("SELECT album_id FROM albums WHERE album_id IN (594,595)")
rows = cur.fetchall()
print(f"Albums remaining: {rows}")

db.close()
print("Done!")
