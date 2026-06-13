import sqlite3

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()

# Check three albums: Porcelain Stars, Greg Mendez, Feeble Little Horse
print('=== Yesterday (2026-06-11) ===')
c.execute("""SELECT album_id, album_name, artist, total_listen_count, cover_image_url 
             FROM albums 
             WHERE artist LIKE '%Porcelain%' OR album_name LIKE '%Rosemary%'""")
print(f'Porcelain Stars - Rosemary: {c.fetchall()}')

c.execute("""SELECT album_id, album_name, artist, total_listen_count, cover_image_url 
             FROM albums 
             WHERE artist LIKE '%Greg Mendez%' OR album_name LIKE '%Beauty Land%'""")
print(f'Greg Mendez - Beauty Land: {c.fetchall()}')

print('\n=== Today (2026-06-12) ===')
c.execute("""SELECT album_id, album_name, artist, total_listen_count, cover_image_url 
             FROM albums 
             WHERE artist LIKE '%Feeble%' OR album_name LIKE '%Bitknot%'""")
print(f'Feeble Little Horse - Bitknot: {c.fetchall()}')

# Check Inundaremos again
print('\n=== Inundaremos - tanquemante (updated today) ===')
c.execute("""SELECT album_id, album_name, artist, total_listen_count 
             FROM albums 
             WHERE album_id = 516""")
print(f'Inundaremos: {c.fetchall()}')

# Summary: total albums count
c.execute("SELECT COUNT(*) FROM albums")
print(f'\nTotal albums in database: {c.fetchone()[0]}')

conn.close()
