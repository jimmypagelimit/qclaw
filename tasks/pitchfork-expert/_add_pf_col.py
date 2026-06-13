"""Check albums table schema and add pitchfork_score column if needed"""
import sqlite3
DB_PATH = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.execute("PRAGMA table_info(albums)")
cols = cur.fetchall()
print("albums table columns:")
for c in cols:
    print(f"  {c[1]} ({c[2]})")

# Check if pitchfork_score exists
names = [c[1] for c in cols]
if 'pitchfork_score' not in names:
    print("\nAdding pitchfork_score column...")
    conn.execute("ALTER TABLE albums ADD COLUMN pitchfork_score REAL")
    conn.commit()
    print("Added!")
else:
    print("\npitchfork_score already exists")

if 'review_url' not in names:
    print("Adding review_url column...")
    conn.execute("ALTER TABLE albums ADD COLUMN review_url TEXT")
    conn.commit()
    print("Added!")
else:
    print("review_url already exists")

conn.close()
