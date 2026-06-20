import sqlite3

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()

# Add status column
c.execute("ALTER TABLE albums ADD COLUMN status TEXT DEFAULT 'active'")
conn.commit()

# Verify
c.execute("PRAGMA table_info(albums)")
cols = [r[1] for r in c.fetchall()]
print('status' in cols)

# Check distribution
c.execute("SELECT status, COUNT(*) FROM albums GROUP BY status")
for r in c.fetchall():
    print(r)

conn.close()
print('Done')
