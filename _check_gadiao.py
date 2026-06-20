import os, sqlite3
DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("SELECT lyrics_text_path FROM tracks WHERE album_id=444 AND lyrics_text_path IS NOT NULL LIMIT 1")
row = c.fetchone()
conn.close()
if row:
    path = row[0]
    print('DB path:', path)
    # 目录内容
    parent = os.path.dirname(path)
    grandparent = os.path.dirname(parent)
    print('Parent:', parent)
    print('Grandparent:', grandparent)
    try:
        entries = os.listdir(grandparent)
        print('Grandparent entries:', len(entries))
        # 找中文目录
        for e in entries:
            if any(ord(c) > 127 for c in e):
                print(' Chinese dir:', e)
                # 列出中文目录内容
                try:
                    sub = os.listdir(os.path.join(grandparent, e))
                    for s in sub:
                        print('  Album:', s)
                        sdir = os.path.join(grandparent, e, s)
                        if os.path.isdir(sdir):
                            files = sorted(os.listdir(sdir))
                            for f in files[:3]:
                                full = os.path.join(sdir, f)
                                if f.endswith('.txt'):
                                    content = open(full, encoding='utf-8').read()
                                    print(f'    {f}: {len(content)} chars')
                                    if content.strip():
                                        print('    Content preview:', content[:100])
                except Exception as ex:
                    print('  Error:', ex)
    except Exception as ex:
        print('Error:', ex)
else:
    print('No path found in DB')
