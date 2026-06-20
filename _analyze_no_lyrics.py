import sqlite3
import os

db_path = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 获取所有完全无歌词的专辑
cur.execute("""SELECT a.album_id, a.album_name, a.artist, a.genre, COUNT(t.id) as track_count
    FROM albums a 
    JOIN tracks t ON a.album_id = t.album_id
    WHERE NOT EXISTS (
        SELECT 1 FROM tracks t2 
        WHERE t2.album_id = a.album_id 
        AND t2.lyrics_text_path IS NOT NULL 
        AND t2.lyrics_text_path != ''
    )
    GROUP BY a.album_id""")

albums = cur.fetchall()

# 分类统计
chinese_albums = []
english_albums = []
genre_stats = {}

for album in albums:
    album_id, album_name, artist, genre, track_count = album
    
    # 判断是中文字段还是英文
    has_chinese = any('\u4e00' <= c <= '\u9fff' for c in album_name + artist)
    
    if has_chinese:
        chinese_albums.append(album)
    else:
        english_albums.append(album)
    
    # 统计流派
    if genre:
        genre_stats[genre] = genre_stats.get(genre, 0) + 1

print(f"=== 完全无歌词专辑分析 ===")
print(f"总计: {len(albums)} 张")
print(f"中文专辑: {len(chinese_albums)} 张")
print(f"英文专辑: {len(english_albums)} 张")

print(f"\n=== 流派分布 (Top 10) ===")
sorted_genres = sorted(genre_stats.items(), key=lambda x: x[1], reverse=True)[:10]
for genre, count in sorted_genres:
    print(f"  {genre}: {count} 张")

# 输出到文件供后续处理
output_path = r'C:\Users\qujt\.qclaw\workspace\_albums_no_lyrics.txt'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(f"完全无歌词专辑列表 ({len(albums)} 张)\n")
    f.write(f"中文: {len(chinese_albums)} | 英文: {len(english_albums)}\n\n")
    
    f.write("=== 中文专辑 ===\n")
    for album in chinese_albums:
        f.write(f"  [{album[0]}] {album[2]} - {album[1]} ({album[4]} tracks) | {album[3]}\n")
    
    f.write("\n=== 英文专辑 ===\n")
    for album in english_albums:
        f.write(f"  [{album[0]}] {album[2]} - {album[1]} ({album[4]} tracks) | {album[3]}\n")

print(f"\n详细列表已保存到: {output_path}")

conn.close()
