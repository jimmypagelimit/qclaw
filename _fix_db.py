import sqlite3, os, time

db_path = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"
journal = db_path + "-journal"

# Remove stale journal
if os.path.exists(journal):
    try:
        os.remove(journal)
        print("Removed journal")
    except Exception as e:
        print(f"Cannot remove journal: {e}")

# Connect with WAL mode
db = sqlite3.connect(db_path, timeout=30)
db.execute("PRAGMA journal_mode=WAL")
mode = db.execute("PRAGMA journal_mode").fetchone()[0]
print(f"Journal mode: {mode}")

# Test write
db.execute("SELECT COUNT(*) FROM albums")
print(f"Albums: {db.execute('SELECT COUNT(*) FROM albums').fetchone()[0]}")

# Test update
db.execute("UPDATE tracks SET lyrics_text_path = lyrics_text_path WHERE id = 1")
db.commit()
print("Write test OK")

db.close()
