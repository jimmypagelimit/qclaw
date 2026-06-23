#!/usr/bin/env python3
"""分步歌词获取 - 每次只查一首"""
import json, os, sys, time, sqlite3, urllib.request, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
LYRICS_DIR = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics'
UA = 'AlbumTracker/1.0'

def sf(s):
    return ''.join(c for c in s if c not in '\\/:*?"<>|').strip()[:120]

conn = sqlite3.connect(DB)

# 找出缺歌词的曲目，每批查少量
batch = int(sys.argv[1]) if len(sys.argv) > 1 else 1
cur = conn.cursor()
cur.execute('''
    SELECT t.id, t.album_id, a.artist, a.album_name, t.track_number, t.track_name
    FROM tracks t JOIN albums a ON t.album_id = a.album_id
    WHERE t.lyrics_lrc_path IS NULL AND t.lyrics_text_path IS NULL
    LIMIT ?
''', (batch,))
rows = cur.fetchall()

if not rows:
    print('NO_MORE')
    conn.close()
    sys.exit()

print('BATCH:%s' % len(rows))
for tid, aid, art, alb, tn, tname in rows:
    url = 'https://lrclib.net/api/search?q=' + urllib.parse.quote(art + ' ' + tname)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        r = urllib.request.urlopen(req, timeout=5)
        d = json.loads(r.read())
        if d:
            lrc = d[0].get('syncedLyrics', '')
            plain = d[0].get('plainLyrics', '')
            base = os.path.join(LYRICS_DIR, sf(art), sf(alb))
            os.makedirs(base, exist_ok=True)
            fn = sf(tname)[:80]
            if lrc:
                p = os.path.join(base, fn + '.lrc')
                open(p, 'w', encoding='utf-8').write(lrc)
                conn.execute('UPDATE tracks SET lyrics_lrc_path=? WHERE id=?', (p, tid))
                print('OK:LRC [%s] %s' % (tn, tname[:30]))
            elif plain:
                p = os.path.join(base, fn + '.txt')
                open(p, 'w', encoding='utf-8').write(plain)
                conn.execute('UPDATE tracks SET lyrics_text_path=? WHERE id=?', (p, tid))
                print('OK:TXT [%s] %s' % (tn, tname[:30]))
            else:
                print('SKIP [%s] %s' % (tn, tname[:30]))
        else:
            print('NONE [%s] %s' % (tn, tname[:30]))
    except Exception as e:
        print('ERR:%s [%s] %s' % (str(e)[:30], tn, tname[:30]))
    time.sleep(0.2)

conn.commit()
conn.close()
print('DONE')
