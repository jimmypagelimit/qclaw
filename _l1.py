#!/usr/bin/env python3
"""只处理1张专辑的缺歌词曲目"""
import json, os, sys, time, sqlite3, urllib.request, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
LYRICS_DIR = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics'

conn = sqlite3.connect(DB)

# 目标专辑ID（从命令行参数读取）
aid = int(sys.argv[1]) if len(sys.argv) > 1 else 0
if not aid:
    print('NEED_ALBUM_ID')
    conn.close()
    sys.exit()

cur2 = conn.cursor()
cur2.execute(
    'SELECT id, track_number, track_name FROM tracks WHERE album_id=? AND lyrics_lrc_path IS NULL AND lyrics_text_path IS NULL ORDER BY disc_number, track_number',
    (aid,))
tracks = cur2.fetchall()

r = conn.execute('SELECT artist, album_name FROM albums WHERE album_id=?', (aid,)).fetchone()
if not r:
    print('ALBUM_NOT_FOUND')
    conn.close()
    sys.exit()

art, alb = r
print('Processing [%s] %s - %s (%s tracks)' % (aid, art, alb, len(tracks)), flush=True)

total_new = 0
for tid, tn, tname in tracks:
    url = 'https://lrclib.net/api/search?q=' + urllib.parse.quote(art[:30] + ' ' + tname[:40])
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'AlbumTracker/1.0'})
        r2 = urllib.request.urlopen(req, timeout=5)
        d = json.loads(r2.read())
        if d:
            lrc = d[0].get('syncedLyrics', '')
            plain = d[0].get('plainLyrics', '')
            base = os.path.join(LYRICS_DIR, ''.join(c for c in art if c not in '\\/:*?"<>|').strip()[:120],
                                ''.join(c for c in alb if c not in '\\/:*?"<>|').strip()[:120])
            os.makedirs(base, exist_ok=True)
            fn = ''.join(c for c in tname if c not in '\\/:*?"<>|').strip()[:80]
            if lrc:
                p = os.path.join(base, fn + '.lrc')
                open(p, 'w', encoding='utf-8').write(lrc)
                conn.execute('UPDATE tracks SET lyrics_lrc_path=? WHERE id=?', (p, tid))
                print('OK [%s] %s' % (tn, tname[:35]), flush=True)
                total_new += 1
            elif plain:
                p = os.path.join(base, fn + '.txt')
                open(p, 'w', encoding='utf-8').write(plain)
                conn.execute('UPDATE tracks SET lyrics_text_path=? WHERE id=?', (p, tid))
                print('OK [%s] %s (txt)' % (tn, tname[:35]), flush=True)
                total_new += 1
            else:
                print('-- [%s] %s' % (tn, tname[:30]), flush=True)
        else:
            print('no [%s] %s' % (tn, tname[:30]), flush=True)
    except Exception as e:
        print('err [%s] %s (%s)' % (tn, tname[:30], str(e)[:25]), flush=True)
    time.sleep(0.2)

conn.commit()
conn.close()
print('NEW:%s' % total_new, flush=True)
