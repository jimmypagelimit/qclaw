import sqlite3, subprocess, shutil, os

DB_LOCAL = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
DB_REMOTE = r'\\10.0.2.4\qemu\原创计划\music\music'
SQL_OUT = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\database.sql'

# Export
conn = sqlite3.connect(DB_LOCAL)
with open(SQL_OUT, 'w', encoding='utf-8') as f:
    for line in conn.iterdump():
        f.write(line + '\n')
conn.close()
print('Exported database.sql')

# Copy to remote
try:
    shutil.copy2(DB_LOCAL, DB_REMOTE)
    print(f'Copied DB to remote: {DB_REMOTE}')
except Exception as e:
    print(f'Remote copy failed: {e}')
