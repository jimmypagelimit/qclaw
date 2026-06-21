import sqlite3
import os

# 导出数据库到 SQL 文件
db_path = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
sql_path = r'C:\Users\qujt\.qclaw\workspace\_music_latest.sql'

# 连接数据库
db = sqlite3.connect(db_path)

# 导出 SQL
with open(sql_path, 'w', encoding='utf-8') as f:
    for line in db.iterdump():
        f.write(line + '\n')

db.close()
print(f"Exported to {sql_path}")
