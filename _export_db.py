import sqlite3, os

DB = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\_music_latest.db'
OUT = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\database.sql'

conn = sqlite3.connect(DB)
with open(OUT, 'w', encoding='utf-8') as f:
    for line in conn.iterdump():
        f.write(line + '\n')

conn.close()
print(f'Exported: {os.path.getsize(OUT)} bytes to {OUT}')
