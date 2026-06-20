import sqlite3
import os

db_path = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 总曲目数
cur.execute('SELECT COUNT(*) FROM tracks')
total_tracks = cur.fetchone()[0]

# 有歌词的曲目数
cur.execute("SELECT COUNT(*) FROM tracks WHERE lyrics_text_path IS NOT NULL AND lyrics_text_path != ''")
tracks_with_lyrics = cur.fetchone()[0]

# 总专辑数
cur.execute('SELECT COUNT(*) FROM albums')
total_albums = cur.fetchone()[0]

# 有歌词的专辑数（至少一首有歌词）
cur.execute("""SELECT COUNT(DISTINCT t.album_id) 
    FROM tracks t 
    WHERE t.lyrics_text_path IS NOT NULL AND t.lyrics_text_path != ''""")
albums_with_lyrics = cur.fetchone()[0]

# 完全无歌词的专辑数
cur.execute("""SELECT COUNT(*) 
    FROM albums a 
    WHERE NOT EXISTS (
        SELECT 1 FROM tracks t 
        WHERE t.album_id = a.album_id 
        AND t.lyrics_text_path IS NOT NULL 
        AND t.lyrics_text_path != ''
    )""")
albums_without_lyrics = cur.fetchone()[0]

print(f"=== 歌词覆盖率统计 ===")
print(f"曲目: {tracks_with_lyrics}/{total_tracks} = {tracks_with_lyrics*100//total_tracks}%")
print(f"专辑: {albums_with_lyrics}/{total_albums} = {albums_with_lyrics*100//total_albums}%")
print(f"完全无歌词专辑: {albums_without_lyrics}")

# 列出完全无歌词的专辑（前20张）
print(f"\n=== 完全无歌词专辑（前20张）===")
cur.execute("""SELECT a.album_id, a.album_name, a.artist, COUNT(t.id) as track_count
    FROM albums a 
    JOIN tracks t ON a.album_id = t.album_id
    WHERE NOT EXISTS (
        SELECT 1 FROM tracks t2 
        WHERE t2.album_id = a.album_id 
        AND t2.lyrics_text_path IS NOT NULL 
        AND t2.lyrics_text_path != ''
    )
    GROUP BY a.album_id
    LIMIT 20""")
for row in cur.fetchall():
    print(f"  [{row[0]}] {row[2]} - {row[1]} ({row[3]} tracks)")

conn.close()
