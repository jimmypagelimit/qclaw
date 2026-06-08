import sqlite3, os

db_path = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
sql_path = r'C:\Users\qujt\.qclaw\workspace\_music_latest.sql'

conn = sqlite3.connect(db_path)
with open(sql_path, 'w', encoding='utf-8') as f:
    for line in conn.iterdump():
        f.write(line + '\n')
conn.close()

size_mb = os.path.getsize(sql_path) / 1024 / 1024
print(f"Exported: {sql_path} ({size_mb:.1f} MB)")
