import sqlite3, json, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('G:/原创计划/music')
conn.row_factory = sqlite3.Row
rows = conn.execute(
    "SELECT album_name, artist, release_year, genre, style, cover_image_url, total_listen_count "
    "FROM albums WHERE total_listen_count > 5 AND cover_image_url IS NOT NULL AND cover_image_url != '' "
    "ORDER BY total_listen_count DESC LIMIT 5"
).fetchall()
for r in rows:
    d = dict(r)
    print(json.dumps(d, ensure_ascii=False))
conn.close()
