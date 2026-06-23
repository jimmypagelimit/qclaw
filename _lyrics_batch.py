#!/usr/bin/env python3
"""逐专辑处理缺歌词的英文专辑"""
import json, os, sys, time, sqlite3, urllib.request, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
LYRICS_DIR = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics'
UA = 'AlbumTracker/1.0'

def sf(s):
    return ''.join(c for c in s if c not in '\\/:*?"<>|').strip()[:120]

conn = sqlite3.connect(DB)

# 目标专辑（缺失最多的英文专辑）
TARGET_IDS = [413, 26, 325, 483, 519, 488, 553, 496, 506, 508,
              191, 202, 44, 40, 117, 120, 125, 128, 147, 158,
              163, 171, 176, 177, 179, 192, 193, 196, 209, 218]

done = int(sys.argv[1]) if len(sys.argv) > 1 else 0
album_ids = TARGET_IDS[done:done+3]  # 每次3张

if not album_ids:
    print('ALL_DONE')
    conn.close()
    sys.exit()

total_new = 0
for aid in album_ids:
    cur2 = conn.cursor()
    cur2.execute(
        'SELECT id, track_number, track_name FROM tracks WHERE album_id=? AND lyrics_lrc_path IS NULL AND lyrics_text_path IS NULL ORDER BY disc_number, track_number',
        (aid,))
    tracks = cur2.fetchall()
    
    r = conn.execute('SELECT artist, album_name FROM albums WHERE album_id=?', (aid,)).fetchone()
    if not r or not tracks:
        continue
    art, alb = r
    print('=== [%s] %s - %s (%s tracks) ===' % (aid, art, alb, len(tracks)))
    
    album_new = 0
    for tid, tn, tname in tracks:
        url = 'https://lrclib.net/api/search?q=' + urllib.parse.quote(art[:30] + ' ' + tname[:40])
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            r2 = urllib.request.urlopen(req, timeout=6)
            d = json.loads(r2.read())
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
                    print('  + [%s] %s' % (tn, tname[:35]))
                    album_new += 1
                elif plain:
                    p = os.path.join(base, fn + '.txt')
                    open(p, 'w', encoding='utf-8').write(plain)
                    conn.execute('UPDATE tracks SET lyrics_text_path=? WHERE id=?', (p, tid))
                    print('  + [%s] %s (txt)' % (tn, tname[:35]))
                    album_new += 1
                else:
                    print('  0 [%s] %s' % (tn, tname[:30]))
            else:
                print('  - [%s] %s' % (tn, tname[:30]))
        except Exception as e:
            print('  x [%s] %s (%s)' % (tn, tname[:30], str(e)[:20]))
        time.sleep(0.2)
    
    conn.commit()
    total_new += album_new
    print('  -> %s new\n' % album_new)

conn.close()
print('TOTAL_NEW: %s' % total_new)
