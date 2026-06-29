import os
import sqlite3

# 数据库路径
db_path = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
lyrics_dir = 'tasks/lyrics-expert/lyrics'

# 连接到数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 获取所有专辑
cursor.execute("SELECT album_name, artist FROM albums")
all_albums = cursor.fetchall()

# 获取已处理的专辑
processed = set()
if os.path.exists(lyrics_dir):
    for artist in os.listdir(lyrics_dir):
        artist_path = os.path.join(lyrics_dir, artist)
        if os.path.isdir(artist_path):
            for album in os.listdir(artist_path):
                album_path = os.path.join(artist_path, album)
                if os.path.isdir(album_path):
                    processed.add((album, artist))

# 找出未处理的
unprocessed = []
for album_name, artist in all_albums:
    if (album_name, artist) not in processed:
        unprocessed.append((album_name, artist))

print(f"数据库中专辑总数: {len(all_albums)}")
print(f"已处理专辑数: {len(processed)}")
print(f"未处理专辑数: {len(unprocessed)}")

if unprocessed:
    print("\n未处理专辑（前20张）:")
    for i, (album_name, artist) in enumerate(unprocessed[:20], 1):
        print(f"{i}. {artist} - {album_name}")
    
    # 保存到文件（避免编码问题）
    with open('unprocessed_albums.txt', 'w', encoding='utf-8') as f:
        f.write(f"未处理专辑总数: {len(unprocessed)}\n\n")
        for i, (album_name, artist) in enumerate(unprocessed, 1):
            f.write(f"{i}. {artist} - {album_name}\n")
    print("\n[OK] 完整列表已保存到 unprocessed_albums.txt")
else:
    print("\n[OK] 所有专辑已处理完成！")

conn.close()
