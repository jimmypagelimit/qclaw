import sqlite3, shutil
src = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
dst = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\_music_latest.db'
shutil.copy2(src, dst)
conn = sqlite3.connect(dst)
cur = conn.cursor()
# list columns first
cur.execute("PRAGMA table_info(albums)")
cols = [r[1] for r in cur.fetchall()]
print("Columns:", cols)
# find by id=123
cur.execute("SELECT * FROM albums WHERE rowid=123")
row = cur.fetchone()
if row:
    print(f"id={row[0]}, name={row[1]}, artist={row[2]}, cover={row[3]}")
# also search for any row with '大只佬'
for i, c in enumerate(cols):
    if 'name' in c.lower() or 'artist' in c.lower():
        print(f"col[{i}]={c}")
conn.close()
