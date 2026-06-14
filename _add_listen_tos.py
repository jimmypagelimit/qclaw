import sqlite3

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()

# Find Teens of Style album_id
cur.execute("SELECT album_id, album_name FROM albums WHERE album_name LIKE '%Teens of Style%'")
row = cur.fetchone()
if not row:
    print("Not found")
else:
    aid = row[0]
    print(f"Found: id={aid} {row[1]}")
    # Insert listen_history record
    cur.execute("""
        INSERT INTO listen_history (album_id, listen_year, listen_date)
        VALUES (?, ?, date('now'))
    """, (aid, 2026))
    print(f"Listen count +1 for album {aid}")
    conn.commit()

conn.close()
print("Done")
