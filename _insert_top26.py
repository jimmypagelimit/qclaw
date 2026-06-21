import sqlite3

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()

new_albums = [
    ('圆缺', '郑宜农', 'TW', 'Asia', 'Indie Pop', 2024),
    ('凝视白色的边界', 'Cicada', 'TW', 'Asia', 'Post-Rock', 2024),
    ('龙年', '华云龙KLE', 'CN', 'Asia', 'Hip-Hop', 2024),
    ('羽毛剑', '秦凡淇', 'CN', 'Asia', 'Pop', 2024),
    ('说出我的名字', 'Tizzy Bac', 'TW', 'Asia', 'Indie Rock', 2024),
    ('Patch', 'Fayzz', 'CN', 'Asia', 'Math Rock', 2024),
    ('生活麻辣烫', '王齐铭WatchMe', 'CN', 'Asia', 'Hip-Hop', 2024),
    ('人人都爱嘻哈乐', '夏之禹', 'CN', 'Asia', 'Hip-Hop', 2024),
    ('TEENAGE RAMBLE', '刘柏辛Lexie', 'CN', 'Asia', 'Pop', 2024),
    ('5689', '超级市场', 'CN', 'Asia', 'Electronic', 2024),
    ('湿地公园', '王啸坤', 'CN', 'Asia', 'Indie Rock', 2024),
    ('ICONOCLASTS', 'Anna Von Hausswolff', 'SE', 'Europe', 'Gothic/Dark Ambient', 2024),
    ('Radio DDR', 'Sharp Pins', 'US', 'North America', 'Indie Rock', 2024),
    ('The Scholars', 'Car Seat Headrest', 'US', 'North America', 'Indie Rock', 2025),
    ('Bleeds', 'Wednesday', 'US', 'North America', 'Indie Rock', 2025),
    ('Ego Death At A Bachelorette Party', 'Hayley Williams', 'US', 'North America', 'Indie Rock', 2025),
    ('Lake Geneva', 'Sophie Zelmani', 'SE', 'Europe', 'Folk', 2024),
    ('Lonely People With Power', 'Deafheaven', 'US', 'North America', 'Black Metal/Post-Metal', 2025),
    ('Instant Holograms On Metal Film', 'Stereolab', 'UK', 'Europe', 'Krautrock/Post-Rock', 2025),
    ('Tavastland', 'Havukruunu', 'FI', 'Europe', 'Black Metal', 2025),
    ('Constellations For The Lonely', 'Doves', 'UK', 'Europe', 'Indie Rock', 2025),
    ('MAYHEM', 'Lady Gaga', 'US', 'North America', 'Pop', 2025),
    ('Glutton For Punishment', 'Heartworms', 'UK', 'Europe', 'Post-Punk', 2025),
]

for album_name, artist, country, region, style, release_year in new_albums:
    c.execute('''INSERT INTO albums (album_name, artist, country, region, style, release_year, status)
                 VALUES (?, ?, ?, ?, ?, ?, 'active')''',
              (album_name, artist, country, region, style, release_year))
    album_id = c.lastrowid
    for i in range(3):
        c.execute('''INSERT INTO listen_history (album_id, listen_date, listen_year, source)
                     VALUES (?, '2025-12-31', 2025, 'top26')''', (album_id,))

# Add listen history for existing 3 albums
for existing_id in [425, 429, 557]:
    for i in range(3):
        c.execute('''INSERT INTO listen_history (album_id, listen_date, listen_year, source)
                     VALUES (?, '2025-12-31', 2025, 'top26')''', (existing_id,))

conn.commit()

c.execute('SELECT COUNT(*) FROM albums')
total = c.fetchone()[0]
c.execute('SELECT MAX(album_id) FROM albums')
max_id = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM listen_history WHERE source='top26'")
lh = c.fetchone()[0]

print(f'Total albums: {total}')
print(f'Max album_id: {max_id}')
print(f'TOP26 listen records: {lh}')

conn.close()
