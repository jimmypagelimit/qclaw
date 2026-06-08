import urllib.request, sqlite3, os

# 网易云找到的专辑和封面URL
albums = [
    (443, 'She Came Back From the Square', '海朋森', 'http://p2.music.126.net/W9LBfy4A5nCwpEU8ku2GHg==/109951163598337609.jpg'),
    (446, '我不要你死于一事无成 No Need for Another History', '海朋森 [Hiperson]', 'http://p2.music.126.net/Wxoz8w8vJBGlmUemTYSC9w==/109951171818269549.jpg')
]

cover_dir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers'
os.makedirs(cover_dir, exist_ok=True)

for album_id, album_name, artist, cover_url in albums:
    # 下载封面
    filename = f'{album_id}-海朋森-{album_name.replace("/", "-")[:50]}.jpg'
    filepath = os.path.join(cover_dir, filename)
    try:
        urllib.request.urlretrieve(cover_url, filepath)
        print(f'Downloaded: {filename}')
    except Exception as e:
        print(f'Failed: {album_name} - {e}')

# 更新数据库
db_path = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

for album_id, album_name, artist, cover_url in albums:
    filename = f'{album_id}-海朋森-{album_name.replace("/", "-")[:50]}.jpg'
    cur.execute('UPDATE albums SET cover_image_url=? WHERE album_id=?', (f'/covers/{filename}', album_id))

conn.commit()
print('Database updated')
conn.close()