import sqlite3

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# Check RYM coverage
cur.execute("""
    SELECT COUNT(*) FROM albums WHERE rym_rating IS NOT NULL
""")
has_rating = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM albums")
total = cur.fetchone()[0]

cur.execute("""
    SELECT album_id, album_name, artist FROM albums 
    WHERE rym_rating IS NULL 
    ORDER BY album_id 
    LIMIT 20
""")
missing = cur.fetchall()

print(f'RYM coverage: {has_rating}/{total} ({has_rating/total*100:.1f}%)')
print(f'Missing: {total - has_rating}')
print('\nFirst 20 missing:')
for r in missing:
    print(f'{r[0]}: {r[2]} - {r[1]}')

conn.close()
