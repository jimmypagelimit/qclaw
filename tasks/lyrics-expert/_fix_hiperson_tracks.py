import sqlite3, sys, time, urllib.request, json
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
cn_release_mbid = '1161da72-d99d-4c50-9407-57940ddbe261'

# Correct Chinese tracklist
chinese_titles = [
    ('春风', 1, 1),
    ('新都人', 2, 1),
    ('我进入了绝望的时期', 3, 1),
    ('每天的行军', 4, 1),
    ('撞进白昼', 5, 1),
    ('从出生到现在', 6, 1),
    ('我们的歌谣', 7, 1),
    ('找到了', 8, 1),
    ('我不愿再有来生', 9, 1),
    ('快乐的时光总是短暂的', 10, 1),
]

# Durations from MusicBrainz (in seconds)
mb_durations = [475, 342, 263, 524, 180, 248, 463, 320, 400, 221]

conn = sqlite3.connect(db)
cur = conn.cursor()

# Set correct MBID
cur.execute("UPDATE albums SET release_mbid = ? WHERE album_id = 424", (cn_release_mbid,))

# Insert correct tracks
for (name, track_num, disc_num), dur in zip(chinese_titles, mb_durations):
    cur.execute("""
        INSERT INTO tracks (album_id, track_number, track_name, duration, disc_number, source)
        VALUES (?, ?, ?, ?, ?, 'musicbrainz')
    """, (424, track_num, name, dur, disc_num))

conn.commit()

# Verify
cur.execute("SELECT track_number, track_name, duration FROM tracks WHERE album_id = 424 ORDER BY track_number")
tracks = cur.fetchall()
for t in tracks:
    print(f'  {t[0]}. {t[1]} ({t[2]}s)')
    
print(f'\nTotal: {len(tracks)} tracks')
print(f'MBID updated to: {cn_release_mbid}')
conn.close()
