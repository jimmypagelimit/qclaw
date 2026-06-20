#!/usr/bin/env python3
# _fill_lyrics_paths_v2.py - 修复中文匹配问题，重新回填歌词路径
# v2: 中文保留拼音首字母，避免 norm 后变成空字符串
import sqlite3, os, re

DB = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"
LYRICS = r"C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics"

def norm(s: str) -> str:
    """归一化：英文小写去特殊字符，中文原样保留但去空格"""
    # 保留所有 Unicode 字母和数字，只去掉标点和空格
    return re.sub(r'[\s\-_\.\(\)\[\]\{\}\,\!\?\:\;\'\"\/\\]', '', s).lower()

def match_file(track_name: str, files: list) -> str | None:
    """匹配曲目名到文件名"""
    tn = norm(track_name)
    # 1. 精确匹配
    for f in files:
        if norm(os.path.splitext(f)[0]) == tn:
            return f
    # 2. 去除数字前缀匹配 (如 "01. 男孩别哭" -> "男孩别哭")
    for f in files:
        base = re.sub(r'^\d+[\.\s]*', '', os.path.splitext(f)[0])
        if norm(base) == tn:
            return f
    # 3. 前 15 字符前缀匹配
    for f in files:
        if norm(os.path.splitext(f)[0]).startswith(tn[:15]):
            return f
    return None

db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row
cur = db.cursor()

# 先清空所有歌词路径（因为 v1 的中文匹配是错的）
cur.execute("UPDATE tracks SET lyrics_text_path = NULL, lyrics_lrc_path = NULL")
db.commit()
print("已清空旧歌词路径")

# 构建歌词目录索引：norm(artist) -> {norm(album): full_path}
dir_index = {}  # norm_artist -> {norm_album: (artist_dir_full, album_dir_full)}
if os.path.isdir(LYRICS):
    for artist_dir in os.listdir(LYRICS):
        artist_path = os.path.join(LYRICS, artist_dir)
        if not os.path.isdir(artist_path):
            continue
        a_key = norm(artist_dir)
        if a_key not in dir_index:
            dir_index[a_key] = {}
        for album_dir in os.listdir(artist_path):
            album_path = os.path.join(artist_path, album_dir)
            if not os.path.isdir(album_path):
                continue
            b_key = norm(album_dir)
            dir_index[a_key][b_key] = album_path

# 获取所有曲目
tracks = cur.execute("""
    SELECT t.id, t.track_number, t.track_name, a.artist, a.album_name, a.album_id
    FROM tracks t
    JOIN albums a ON a.album_id = t.album_id
""").fetchall()

print(f"待处理曲目: {len(tracks)}")

updated = 0
no_artist = 0
no_album = 0
no_file = 0

for row in tracks:
    tid = row['id']
    tname = row['track_name']
    artist = row['artist']
    album = row['album_name']
    aid = row['album_id']

    a_key = norm(artist)
    b_key = norm(album)

    # 查找艺人目录
    if a_key not in dir_index:
        # 尝试模糊：检查 dir_index 中是否有包含 artist 的 key
        found = False
        for dk in dir_index:
            if a_key in dk or dk in a_key:
                a_key = dk
                found = True
                break
        if not found:
            no_artist += 1
            continue

    # 查找专辑目录
    album_dirs = dir_index.get(a_key, {})
    if b_key not in album_dirs:
        # 模糊
        found = False
        for dk in album_dirs:
            if b_key in dk or dk in b_key:
                b_key = dk
                found = True
                break
        if not found:
            no_album += 1
            continue

    matched_dir = album_dirs[b_key]
    files = os.listdir(matched_dir)

    txt_file = match_file(tname, [f for f in files if f.endswith('.txt')])
    lrc_file = match_file(tname, [f for f in files if f.endswith('.lrc')])

    txt_path = os.path.join(matched_dir, txt_file) if txt_file else None
    lrc_path = os.path.join(matched_dir, lrc_file) if lrc_file else None

    if txt_path or lrc_path:
        cur.execute(
            "UPDATE tracks SET lyrics_text_path=?, lyrics_lrc_path=? WHERE id=?",
            (txt_path, lrc_path, tid)
        )
        updated += 1
    else:
        no_file += 1

db.commit()
print(f"更新完成: {updated}/{len(tracks)}")
print(f"无艺人目录: {no_artist}, 无专辑目录: {no_album}, 无歌词文件: {no_file}")

# 统计
total = cur.execute("SELECT COUNT(*) FROM tracks").fetchone()[0]
has = cur.execute("SELECT COUNT(*) FROM tracks WHERE lyrics_text_path IS NOT NULL OR lyrics_lrc_path IS NOT NULL").fetchone()[0]
print(f"总曲目: {total}, 有歌词: {has} ({has*100//total}%)")

# 有歌词的专辑数
lyric_albums = cur.execute("SELECT COUNT(DISTINCT album_id) FROM tracks WHERE lyrics_text_path IS NOT NULL OR lyrics_lrc_path IS NOT NULL").fetchone()[0]
total_albums_with_tracks = cur.execute("SELECT COUNT(DISTINCT album_id) FROM tracks").fetchone()[0]
print(f"有曲目专辑: {total_albums_with_tracks}, 有歌词专辑: {lyric_albums}")

db.close()
