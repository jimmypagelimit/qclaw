import sqlite3

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
c = conn.cursor()

with open(r'C:\Users\qujt\.qclaw\workspace\_country_region_details.txt', 'w', encoding='utf-8') as f:
    queries = [
        ("XW (3张)", "SELECT album_id, album_name, artist, country FROM albums WHERE country='XW'"),
        ("Worldwide (2张)", "SELECT album_id, album_name, artist, country FROM albums WHERE country='Worldwide'"),
        ("空字符串 (23张)", "SELECT album_id, album_name, artist, country FROM albums WHERE country=''"),
        ("None (8张)", "SELECT album_id, album_name, artist, country FROM albums WHERE country IS NULL"),
        ("US (17张)", "SELECT album_id, album_name, artist, country FROM albums WHERE country='US'"),
        ("UK (4张)", "SELECT album_id, album_name, artist, country FROM albums WHERE country='UK'"),
        ("China (6张)", "SELECT album_id, album_name, artist, country FROM albums WHERE country='China'"),
        ("Germany (3张)", "SELECT album_id, album_name, artist, country FROM albums WHERE country='Germany'"),
        ("Taiwan (2张)", "SELECT album_id, album_name, artist, country FROM albums WHERE country='Taiwan'"),
        ("Europe (2张)", "SELECT album_id, album_name, artist, country FROM albums WHERE country='Europe'"),
    ]
    
    for label, sql in queries:
        f.write(f'\n=== {label} ===\n')
        c.execute(sql)
        for r in c.fetchall():
            f.write(f'  id={r[0]}, {r[2]} - {r[1]}, country={repr(r[3])}\n')

conn.close()
print('Done - check _country_region_details.txt')
