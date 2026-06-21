import sqlite3

DB_PATH = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'

# 25 albums from 2025 TOP26, excluding 灰太阳 (already in DB as ID=425)
new_albums = [
    {"album_name": "Rgyagdzie!", "artist": "Smiqra", "release_year": 2025, "genre": "Avant-Garde Metal", "style": "Technical Thrash Metal, Progressive Metal, Mathcore, Brutal Prog, Dissonant Black Metal", "rym_rating": 3.49, "rym_ratings_count": 827},
    {"album_name": "Head 7", "artist": "DJ小女孩", "release_year": 2025, "genre": "Electro House", "style": "Post-Industrial, Dark Ambient, Art Pop, Deconstructed Club, Witch House", "rym_rating": 3.47, "rym_ratings_count": 306},
    {"album_name": "people", "artist": "jackapplepeople", "release_year": 2025, "genre": "Contemporary Folk", "style": "Singer-Songwriter, Indie Folk", "rym_rating": 3.38, "rym_ratings_count": 240},
    {"album_name": "Quit Quietly", "artist": "落日飞车", "release_year": 2025, "genre": "Soft Rock", "style": "Indie Pop, Sophisti-Pop", "rym_rating": 3.37, "rym_ratings_count": 178},
    {"album_name": "Fleeting Hearts", "artist": "FiFi Zhang", "release_year": 2025, "genre": "Dance-Pop", "style": "House, Deep House, 2-Step Garage House", "rym_rating": 3.44, "rym_ratings_count": 137},
    {"album_name": "疼痛部", "artist": "v是兔子", "release_year": 2025, "genre": "Slacker Rock", "style": "Midwest Emo, Slowcore, Post-Rock, Screamo, Shoegaze", "rym_rating": 3.42, "rym_ratings_count": 124},
    {"album_name": "如果每天都可以 Happy Happy 谁想要Sad:)) – 一起去度假", "artist": "陈娴静", "release_year": 2025, "genre": "Bedroom Pop", "style": "Sophisti-Pop, Pop Rap, Dream Pop", "rym_rating": 3.56, "rym_ratings_count": 104},
    {"album_name": "Moon Phases", "artist": "郑宜农", "release_year": 2025, "genre": "Art Pop", "style": "Electronic, Ambient Pop, Chillwave, Breakbeat, Synthwave", "rym_rating": 3.46, "rym_ratings_count": 96},
    {"album_name": "凝视白色的边界", "artist": "Cicada", "release_year": 2025, "genre": "Chamber Music", "style": "Neoclassical, New Age", "rym_rating": 3.54, "rym_ratings_count": 73},
    {"album_name": "A Fish Under the Pillow", "artist": "Yikii", "release_year": 2025, "genre": "Microtonal Classical", "style": "Electronic, Sequencer & Tracker, Chinese Classical Music, Post-Industrial, Noise", "rym_rating": 3.49, "rym_ratings_count": 80},
    {"album_name": "LVL R", "artist": "R!R!Riot", "release_year": 2025, "genre": "Trap", "style": "Cloud Rap", "rym_rating": 3.47, "rym_ratings_count": 94},
    {"album_name": "Pleasure", "artist": "蔡依林", "release_year": 2025, "genre": "Contemporary R&B", "style": "Electropop, Alt-Pop, Alternative R&B, Electronic Dance Music", "rym_rating": 3.02, "rym_ratings_count": 129},
    {"album_name": "A Lucid Dream Last Night", "artist": "An Empty City", "release_year": 2025, "genre": "Metalcore", "style": "Alternative Metal, Nu Metal", "rym_rating": 3.41, "rym_ratings_count": 72},
    {"album_name": "人人都爱嘻哈乐", "artist": "夏之禹", "release_year": 2025, "genre": "Boom Bap", "style": "Jazz Rap, Lo-Fi Hip Hop, Conscious Hip Hop", "rym_rating": 3.71, "rym_ratings_count": 69},
    {"album_name": "幽默与笑话", "artist": "卡力老虎", "release_year": 2025, "genre": "Comedy Rap", "style": "Pop Rap, Jerk Rage Trap", "rym_rating": 3.62, "rym_ratings_count": 76},
    {"album_name": "Earcandy", "artist": "Miso Extra", "release_year": 2025, "genre": "Alternative R&B", "style": "Alt-Pop, Pop Rap, Dance-Pop, UK Garage, Hip House, Hyperpop", "rym_rating": 3.08, "rym_ratings_count": 86},
    {"album_name": "Serpents and Shallows", "artist": "Thisquietarmy", "release_year": 2025, "genre": "Drone", "style": "Noise, Chinese Folk Music", "rym_rating": 3.46, "rym_ratings_count": 59},
    {"album_name": "Vooid 2025", "artist": "VOOID", "release_year": 2025, "genre": "Indie Rock", "style": "Noise Rock", "rym_rating": 3.59, "rym_ratings_count": 61},
    {"album_name": "Old Tales Retold", "artist": "颜峻", "release_year": 2025, "genre": "Free Improvisation", "style": "Onkyo", "rym_rating": 3.61, "rym_ratings_count": 40},
    {"album_name": "The Beneficial Society", "artist": "有益社会", "release_year": 2025, "genre": "Midwest Emo", "style": "Emo, Screamo, Jazz-Rock, Art Punk, Post-Hardcore", "rym_rating": 3.55, "rym_ratings_count": 58},
    {"album_name": "Heal Me Good", "artist": "Yufu", "release_year": 2025, "genre": "Progressive Soul", "style": "Funk, Psychedelic Soul, Motown Sound", "rym_rating": 3.49, "rym_ratings_count": 50},
    {"album_name": "未完", "artist": "时过夏末", "release_year": 2025, "genre": "Post-Rock", "style": "", "rym_rating": 3.46, "rym_ratings_count": 47},
    {"album_name": "赵小六的舌头", "artist": "赵小六", "release_year": 2025, "genre": "Hanmai", "style": "Electronic Dance Music, Nightcore, Speedcore", "rym_rating": 3.45, "rym_ratings_count": 64},
    {"album_name": "究极之境", "artist": "九宝", "release_year": 2025, "genre": "Folk Metal", "style": "", "rym_rating": 3.28, "rym_ratings_count": 58},
]

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Get max album_id
c.execute("SELECT MAX(album_id) FROM albums")
max_id = c.fetchone()[0]
print(f"Current max album_id: {max_id}")

# Get all artist names for reference
c.execute("SELECT artist_id, name FROM artists WHERE name IS NOT NULL")
artists = {r[1]: r[0] for r in c.fetchall()}

inserted = 0
for album in new_albums:
    max_id += 1
    # check artist exists
    artist_name = album["artist"]
    artist_id = artists.get(artist_name)
    
    c.execute("""
        INSERT INTO albums (album_id, album_name, artist, release_year, genre, style, rym_rating, rym_ratings_count, artist_id, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
    """, (
        max_id, album["album_name"], artist_name, album["release_year"],
        album["genre"], album["style"], album["rym_rating"], album["rym_ratings_count"], artist_id
    ))
    
    # Add listen_history: 3 listens on 2025-12-31
    for i in range(3):
        c.execute("""
            INSERT INTO listen_history (album_id, listen_date, listen_year, notes, source)
            VALUES (?, '2025-12-31', 2025, '2025个人TOP26', 'top26')
        """, (max_id,))
    
    inserted += 1
    print(f"  [{inserted}/24] {artist_name} - {album['album_name']} (ID={max_id})")

conn.commit()

# Verify
c.execute("SELECT COUNT(*) FROM albums")
total = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM listen_history")
lh_total = c.fetchone()[0]
print(f"\nDone! Total albums: {total}, Total listen_history: {lh_total}")

conn.close()
