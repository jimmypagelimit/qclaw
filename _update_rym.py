import json, sqlite3

db_path = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 加 RYM 字段
cur.execute('ALTER TABLE albums ADD COLUMN rym_rating REAL')
cur.execute('ALTER TABLE albums ADD COLUMN rym_ratings_count INTEGER')
cur.execute('ALTER TABLE albums ADD COLUMN rym_url TEXT')
conn.commit()
print('Columns added')

# 读取 RYM 批量结果
data = json.load(open(r'C:\Users\qujt\.qclaw\workspace\rym_batch_results.json', encoding='utf-8'))
updated = 0
for item in data:
    if 'error' in item or not item.get('rym_rating'):
        continue
    cur.execute(
        'UPDATE albums SET rym_rating=?, rym_ratings_count=?, rym_url=? WHERE album_name=? AND artist=?',
        (item.get('rym_rating', 0) or 0, item.get('rym_ratings_count', 0) or 0, item.get('rym_url', '') or '',
         item.get('album_name'), item.get('artist'))
    )
    updated += 1

conn.commit()
print(f'Updated {updated} albums')
conn.close()