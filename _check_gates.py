import sqlite3

db_path = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Search for 'Ghost of a Future Dead' or 'At The Gates'
cur.execute("""
    SELECT album_id, album_name, artist FROM albums 
    WHERE album_name LIKE '%Ghost%' OR album_name LIKE '%At The Gates%' OR album_name LIKE '%Drink from the Night%'
""")
rows = cur.fetchall()
for r in rows:
    print('ID:', r[0], '| Album:', r[1], '| Artist:', r[2])

cur.execute("SELECT COUNT(*) FROM albums WHERE artist LIKE '%At The Gates%'")
print('At The Gates albums count:', cur.fetchone()[0])

# Also search by artist
cur.execute("SELECT album_id, album_name, artist FROM albums WHERE artist LIKE '%Gates%'")
print('Gates matches:')
for r in cur.fetchall():
    print('  ID:', r[0], '| Album:', r[1], '| Artist:', r[2])

# List all At The Gates or similar death metal
cur.execute("SELECT album_id, album_name, artist FROM albums WHERE artist LIKE '%Gates%' OR artist LIKE '%Gates%'")
print('---')

conn.close()
