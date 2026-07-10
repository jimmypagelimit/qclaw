import sqlite3, os, datetime

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()

# 有Pitchfork评分的专辑
cur.execute("SELECT album_id, artist, album_name, pitchfork_score, release_year FROM albums WHERE pitchfork_score > 0 ORDER BY release_year DESC")
rows = cur.fetchall()
print('Pitchfork评分专辑 (%d张):' % len(rows))
for r in rows:
    print('  ID=%d | %s | %s | %.1f | %s' % (r[0], r[1][:22], r[2][:22], r[3], r[4]))

# pitchfork-expert翻译目录
PEX = r'C:\Users\qujt\.qclaw\workspace\tasks\pitchfork-expert\docs\zh'
if os.path.exists(PEX):
    docs = []
    for root, dirs, files in os.walk(PEX):
        for f in files:
            if f.endswith('.md'):
                path = os.path.join(root, f)
                mtime = os.path.getmtime(path)
                docs.append((mtime, f, root))
    docs.sort(reverse=True)
    print('\nPitchfork Expert 翻译 (最近15篇):')
    for mtime, f, root in docs[:15]:
        dt = datetime.datetime.fromtimestamp(mtime)
        print('  %s | %s' % (str(dt)[:10], f))
    print('  共 %d 篇' % len(docs))
else:
    print('pitchfork-expert 目录不存在')

# pitchfork-expert 根目录
PROOT = r'C:\Users\qujt\.qclaw\workspace\tasks\pitchfork-expert'
if os.path.exists(PROOT):
    print('\npitchfork-expert 根目录:')
    for f in os.listdir(PROOT):
        print(' ', f)
else:
    print('pitchfork-expert 根目录不存在')

conn.close()
