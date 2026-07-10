import sqlite3
DB = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"
db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row

# Check listen_history schema
cols = db.execute("PRAGMA table_info(listen_history)").fetchall()
print("listen_history columns:", [(c['name'], c['type']) for c in cols])

# Check sample
rows = db.execute("SELECT * FROM listen_history LIMIT 3").fetchall()
if rows:
    print("Sample row keys:", rows[0].keys())
    for r in rows:
        print(dict(r))
db.close()
