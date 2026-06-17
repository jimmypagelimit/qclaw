import sqlite3
db = sqlite3.connect(r"C:\Users\qujt\.qclaw\workspace\_music_latest.db")
tables = db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
for t in tables:
    print(t[0])
# Also check if there's a tracks/songs table
for t in tables:
    name = t[0]
    columns = [c[1] for c in db.execute(f"PRAGMA table_info({name})").fetchall()]
    if any(kw in name for kw in ["track", "song", "trac", "曲目", "tracklist"]):
        print(f"\n  {name} columns: {columns}")
        print(f"  row count: {db.execute(f'SELECT COUNT(*) FROM {name}').fetchone()[0]}")
db.close()
