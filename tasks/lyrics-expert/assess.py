import os, sqlite3

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
LYRICS_DIR = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics'
OUT = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\assess_result.txt'

lines = []

# 已有歌词的专辑
existing_dirs = set()
for artist_dir in os.listdir(LYRICS_DIR):
    ap = os.path.join(LYRICS_DIR, artist_dir)
    if os.path.isdir(ap):
        for album_dir in os.listdir(ap):
            bp = os.path.join(ap, album_dir)
            if os.path.isdir(bp):
                lrc_count = len([f for f in os.listdir(bp) if f.endswith('.lrc')])
                if lrc_count:
                    existing_dirs.add((artist_dir, album_dir, lrc_count))

lines.append(f"已有歌词的专辑: {len(existing_dirs)}\n")
for a_name, al_name, count in sorted(existing_dirs):
    lines.append(f"  {a_name} - {al_name} ({count} LRC)\n")

conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("""
    SELECT a.album_id, a.artist, a.album_name,
           (SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id) as pc
    FROM albums a
    WHERE a.album_name != ''
    ORDER BY pc DESC
""")
rows = cur.fetchall()
conn.close()

def has_chinese(s):
    return any('\u4e00' <= c <= '\u9fff' for c in s)

def safe(s):
    return ''.join(c for c in str(s) if c not in r'\/:*?"<>|').strip()

# 找未处理的
need_lyrics = []
for album_id, artist, album, pc in rows:
    a_name = safe(artist)
    al_name = safe(album)
    already = False
    for ea, eal, _ in existing_dirs:
        if ea.lower() == a_name.lower() and (eal.lower() == al_name.lower() or eal.lower() in al_name.lower() or al_name.lower() in eal.lower()):
            already = True
            break
    if not already:
        is_cn = has_chinese(artist) or has_chinese(album)
        need_lyrics.append((pc, album_id, artist, album, '中文' if is_cn else '英文'))

need_lyrics.sort(key=lambda x: -x[0])
cn_albums = [(a_id, art, alb) for pc, a_id, art, alb, lang in need_lyrics if lang == '中文']
en_albums = [(a_id, art, alb) for pc, a_id, art, alb, lang in need_lyrics if lang == '英文']

lines.append(f"\n需要获取歌词: {len(need_lyrics)} 张专辑\n")
lines.append(f"  中文: {len(cn_albums)} 张\n")
lines.append(f"  英文: {len(en_albums)} 张\n")

lines.append("\n=== 中文专辑（前30）===\n")
for i, (a_id, art, alb) in enumerate(cn_albums[:30], 1):
    pc = next((p for p, aid, _, _, _ in need_lyrics if aid == a_id), 0)
    lines.append(f"  {i:2d}. [{pc:2d}] {art} - {alb} (id={a_id})\n")

lines.append(f"\n... 共 {len(cn_albums)} 张中文专辑\n")

lines.append("\n=== 英文专辑（前20）===\n")
for i, (a_id, art, alb) in enumerate(en_albums[:20], 1):
    pc = next((p for p, aid, _, _, _ in need_lyrics if aid == a_id), 0)
    lines.append(f"  {i:2d}. [{pc:2d}] {art} - {alb} (id={a_id})\n")

with open(OUT, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Done")
