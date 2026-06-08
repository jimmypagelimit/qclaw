import json, sqlite3

db_path = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

data = json.load(open(r'C:\Users\qujt\.qclaw\workspace\rym_batch_results.json', encoding='utf-8'))
updated = 0
skipped = 0
for item in data:
    if 'error' in item or not item.get('rym_rating'):
        continue
    album_name = item.get('album_name', '')
    artist = item.get('artist', '')
    rym_rating = item.get('rym_rating', 0) or 0
    rym_ratings_count = item.get('rym_ratings_count', 0) or 0
    rym_url = item.get('rym_url', '') or ''

    if artist:
        cur.execute(
            'UPDATE albums SET rym_rating=?, rym_ratings_count=?, rym_url=? WHERE album_name=? AND artist=?',
            (rym_rating, rym_ratings_count, rym_url, album_name, artist)
        )
    else:
        cur.execute(
            'UPDATE albums SET rym_rating=?, rym_ratings_count=?, rym_url=? WHERE album_name=?',
            (rym_rating, rym_ratings_count, rym_url, album_name)
        )
    updated += 1

conn.commit()
print(f'Updated {updated} albums')
conn.close()