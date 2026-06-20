import sqlite3

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Check the 6 conflict artists: what countries are in their albums
conflicts = ['Paul McCartney', 'The Cure', 'Tizzy Bac', 'U2', '张雨生', '陈楚生']

with open(r'C:\Users\qujt\.qclaw\workspace\_conflict_details.txt', 'w', encoding='utf-8') as f:
    for artist in conflicts:
        f.write(f'=== {artist} ===\n')
        c.execute('''
        SELECT album_name, country, region
        FROM albums
        WHERE artist = ?
        ORDER BY album_name
        ''', (artist,))
        for row in c.fetchall():
            f.write(f'  {row["album_name"]}: country={row["country"]}, region={row["region"]}\n')
        f.write('\n')

conn.close()
print('Done - see _conflict_details.txt')
