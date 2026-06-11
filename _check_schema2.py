import sqlite3
db = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\_music_latest.db'
conn = sqlite3.connect(db)
cur = conn.cursor()
# Check existing styles
cur.execute("SELECT style_id, name FROM styles ORDER BY name")
styles = cur.fetchall()
for s in styles:
    print(f"  {s[0]}: {s[1]}")

# Check genres
cur.execute("SELECT genre_id, name FROM genres ORDER BY name")
genres = cur.fetchall()
for g in genres:
    print(f"  genre {g[0]}: {g[1]}")

# Check if Greg Mendez artist exists
cur.execute("SELECT artist_id, name FROM artists WHERE name LIKE '%Greg%'")
for a in cur.fetchall():
    print(f"  artist: {a}")

# Also check listen_history table structure
cur.execute("PRAGMA table_info(listen_history)")
for c in cur.fetchall():
    print(f"  lh col: {c}")
conn.close()
