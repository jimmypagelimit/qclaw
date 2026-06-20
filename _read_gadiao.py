import os, sqlite3

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
LYRICS = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics'

conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("SELECT lyrics_text_path, lyrics_lrc_path FROM tracks WHERE album_id=444 AND lyrics_lrc_path IS NOT NULL LIMIT 3")
rows = c.fetchall()
conn.close()

for txt_path, lrc_path in rows:
    if lrc_path and os.path.exists(lrc_path):
        content = open(lrc_path, encoding='utf-8').read()
        fname = os.path.basename(lrc_path)
        print(f'File: {fname}')
        print(f'Size: {len(content)} chars')
        print('First 3 lines:')
        for line in content.split('\n')[:3]:
            print(f'  {line}')
        print()
    elif txt_path and os.path.exists(txt_path):
        content = open(txt_path, encoding='utf-8').read()
        fname = os.path.basename(txt_path)
        print(f'File: {fname}')
        print(f'Size: {len(content)} chars')
        print('First 3 lines:')
        for line in content.split('\n')[:3]:
            print(f'  {line}')
        print()
