import sqlite3

db_path = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查 tracks 表结构
cursor.execute("PRAGMA table_info(tracks)")
columns = cursor.fetchall()

print("tracks 表结构:")
for col in columns:
    print(f"  {col[1]:20s} {col[2]}")

# 查看一条样本数据
cursor.execute("SELECT * FROM tracks LIMIT 1")
row = cursor.fetchone()

print("\n样本数据:")
if row:
    for i, col in enumerate(columns):
        print(f"  {col[1]}: {row[i]}")

conn.close()
