import sqlite3
import os

db_path = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\data\covers.db"

if not os.path.exists(db_path):
    print("Database not found")
    exit(1)

conn = sqlite3.connect(db_path)
c = conn.cursor()

# Check tables
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
print(f"Tables: {tables}")

# Try to count covers if albums table exists
try:
    c.execute("SELECT COUNT(*) FROM albums WHERE cover_path IS NOT NULL")
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM albums WHERE cover_path IS NULL")
    remaining = c.fetchone()[0]
    print(f"Total with covers: {total}")
    print(f"Remaining: {remaining}")
except Exception as e:
    print(f"Error querying albums: {e}")

conn.close()
