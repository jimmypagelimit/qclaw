import sqlite3

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Step 1: Add region column to artists
try:
    c.execute("ALTER TABLE artists ADD COLUMN region TEXT DEFAULT ''")
    print('Added region column to artists')
except Exception as e:
    print(f'region column may already exist: {e}')

# Step 2: Migrate country/region from albums -> artists
# For each artist, take the most common non-empty country/region from their albums
c.execute('''
SELECT a.artist_id, a.name,
       ar.country, ar.region
FROM artists a
LEFT JOIN albums ar ON ar.artist = a.name
WHERE (ar.country IS NOT NULL AND ar.country != '')
   OR (ar.region IS NOT NULL AND ar.region != '')
GROUP BY a.artist_id, ar.country, ar.region
ORDER BY a.artist_id, COUNT(*) DESC
''')
rows = c.fetchall()

# Build mapping: artist_id -> (country, region), prefer most frequent
artist_data = {}
for row in rows:
    aid = row['artist_id']
    country = row['country'] or ''
    region = row['region'] or ''
    if aid not in artist_data:
        artist_data[aid] = (country, region)

# Step 3: Update artists table
updated = 0
for aid, (country, region) in artist_data.items():
    if country or region:
        c.execute('UPDATE artists SET country=?, region=? WHERE artist_id=?', (country, region, aid))
        updated += 1

conn.commit()

# Step 4: Verify
c.execute("SELECT artist_id, name, country, region FROM artists WHERE country != '' OR region != '' LIMIT 10")
with open(r'C:\Users\qujt\.qclaw\workspace\_migrate_verify.txt', 'w', encoding='utf-8') as f:
    f.write(f'Migrated {updated} artists\n\n')
    for row in c.fetchall():
        f.write(f'id={row[0]}, {row[1]}: country={row[2]}, region={row[3]}\n')

# Step 5: Count how many artists have no country/region
c.execute("SELECT COUNT(*) FROM artists WHERE country IS NULL OR country = ''")
empty = c.fetchone()[0]
with open(r'C:\Users\qujt\.qclaw\workspace\_migrate_verify.txt', 'a', encoding='utf-8') as f:
    f.write(f'\nArtists with no country: {empty}\n')

# Step 6: Check for conflicts (same artist name with different country in albums)
c.execute('''
SELECT ar.artist, COUNT(DISTINCT ar.country) as cnt
FROM albums ar
WHERE ar.country IS NOT NULL AND ar.country != ''
GROUP BY ar.artist
HAVING cnt > 1
''')
conflicts = c.fetchall()
with open(r'C:\Users\qujt\.qclaw\workspace\_migrate_verify.txt', 'a', encoding='utf-8') as f:
    f.write(f'\nArtists with conflicting countries: {len(conflicts)}\n')
    for row in conflicts:
        f.write(f'  {row[0]}: {row[1]} different countries\n')

conn.close()
print('Done')
