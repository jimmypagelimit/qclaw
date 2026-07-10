import sqlite3
conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM tracks')
total = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM tracks WHERE lyrics_text_path IS NOT NULL AND lyrics_text_path != ''")
has_text = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM tracks WHERE lyrics_lrc_path IS NOT NULL AND lyrics_lrc_path != ''")
has_lrc = cur.fetchone()[0]
print(f'总曲目: {total}')
print(f'有歌词文本: {has_text} ({has_text*100//total}%)')
print(f'有LRC: {has_lrc} ({has_lrc*100//total}%)')
print(f'缺歌词: {total - has_text} 首')
conn.close()
