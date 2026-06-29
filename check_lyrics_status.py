import sqlite3
import os
from pathlib import Path

db_path = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
lyrics_base = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics'

# 连接数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 获取所有专辑
cursor.execute("SELECT album_name, artist FROM albums")
albums = cursor.fetchall()

print(f"数据库专辑总数: {len(albums)}")
print("="*60)

# 统计有歌词的专辑
lyrics_found = []
lyrics_missing = []

for album_name, artist in albums:
    # 清理专辑名和艺人名（去除尾部空格）
    artist_clean = artist.strip() if artist else artist
    album_clean = album_name.strip() if album_name else album_name
    
    # 检查歌词目录是否存在
    artist_dir = Path(lyrics_base) / artist_clean
    album_dir = artist_dir / album_clean
    
    try:
        if album_dir.exists() and any(album_dir.iterdir()):
            # 目录存在且有文件
            lrc_count = len(list(album_dir.glob("*.lrc")))
            lyrics_found.append((artist_clean, album_clean, lrc_count))
        else:
            lyrics_missing.append((artist_clean, album_clean))
    except Exception as e:
        print(f"  警告: 检查 {artist} - {album_name} 时出错: {e}")
        lyrics_missing.append((artist_clean, album_clean))

print(f"[OK] 有歌词的专辑: {len(lyrics_found)} ({len(lyrics_found)/len(albums)*100:.1f}%)")
print(f"[MISSING] 缺失歌词的专辑: {len(lyrics_missing)} ({len(lyrics_missing)/len(albums)*100:.1f}%)")
print("="*60)

# 显示一些未处理的专辑（西方艺人优先）
print("\n待处理专辑示例（前10张）:")
for i, (artist, album) in enumerate(lyrics_missing[:10]):
    print(f"  {i+1}. {artist} - {album}")

# 保存完整列表到文件
with open(r'C:\Users\qujt\.qclaw\workspace\missing_lyrics.txt', 'w', encoding='utf-8') as f:
    f.write(f"缺失歌词的专辑列表 ({len(lyrics_missing)} 张)\n")
    f.write("="*60 + "\n")
    for i, (artist, album) in enumerate(lyrics_missing):
        f.write(f"{i+1}. {artist} - {album}\n")

print(f"\n完整列表已保存到: missing_lyrics.txt")

conn.close()
