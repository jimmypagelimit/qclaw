# -*- coding: utf-8 -*-
"""歌词计划 - 极简版，每次只处理2张专辑，每张专辑逐曲搜索"""
import sqlite3, urllib.request, urllib.parse, json, time, os, sys, re, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
LYR = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics'

def lrclib(art, trk):
    try:
        url = f"https://lrclib.net/api/search?q={urllib.parse.quote(f'{art} {trk}')}"
        r = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=15)
        d = json.loads(r.read().decode())
        if d:
            for i in d:
                ia = (i.get('artistName') or '').lower()
                it = (i.get('trackName') or '').lower()
                if (art.lower() in ia or ia in art.lower()) and (trk.lower() in it or it in trk.lower()):
                    if i.get('syncedLyrics') or i.get('plainLyrics'):
                        return i.get('syncedLyrics'), i.get('plainLyrics')
            for i in d:
                if i.get('syncedLyrics') or i.get('plainLyrics'):
                    return i.get('syncedLyrics'), i.get('plainLyrics')
    except: pass
    return None, None

def netease(art, trk):
    for q in [trk, f"{art} {trk}"]:
        try:
            url = f"https://music.163.com/api/search/get?s={urllib.parse.quote(q)}&type=1&limit=5"
            r = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0','Referer':'https://music.163.com/'}), timeout=15)
            d = json.loads(r.read().decode())
            if d.get('code')==200 and d.get('result',{}).get('songs'):
                for s in d['result']['songs'][:5]:
                    sn = s.get('name','')
                    if trk.lower() in sn.lower() or sn.lower() in trk.lower():
                        sid = s['id']
                        lurl = f"https://music.163.com/api/song/lyric?id={sid}&lv=1"
                        r2 = urllib.request.urlopen(urllib.request.Request(lurl, headers={'User-Agent':'Mozilla/5.0','Referer':'https://music.163.com/'}), timeout=15)
                        ld = json.loads(r2.read().decode())
                        lrc = ld.get('lrc',{}).get('lyric','')
                        if lrc and lrc.strip():
                            plain = re.sub(r'\[\d+:\d+\.\d+\]','',lrc).strip()
                            return lrc, plain
        except: pass
        time.sleep(0.3)
    return None, None

def sfn(n):
    return re.sub(r'[<>:"/\\|?*]','',n or 'unknown').strip()

def save(art, alb, trk, lrc, txt):
    d = os.path.join(LYR, sfn(art), sfn(f"{art} {alb}"))
    os.makedirs(d, exist_ok=True)
    bn = sfn(trk)
    lp = tp = ''
    if lrc:
        lp = os.path.join(d, f"{bn}.lrc")
        with open(lp,'w',encoding='utf-8') as f: f.write(lrc)
    if txt:
        tp = os.path.join(d, f"{bn}.txt")
        with open(tp,'w',encoding='utf-8') as f: f.write(txt)
    return lp, tp

def main():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    
    # Get 2 albums with most missing lyrics
    c.execute("""SELECT a.album_id, a.artist, a.album_name, a.country
                  FROM tracks t JOIN albums a ON t.album_id = a.album_id
                  WHERE (t.lyrics_text_path IS NULL OR t.lyrics_text_path='')
                    AND (t.lyrics_lrc_path IS NULL OR t.lyrics_lrc_path='')
                  HAVING COUNT(*) > 0
                  ORDER BY CASE WHEN a.country IN ('中国','台湾','香港') THEN 0 ELSE 1 END, COUNT(*) DESC
                  LIMIT 2""")
    
    albums = c.fetchall()
    found = missed = 0
    
    for aid, art, alb, co in albums:
        c.execute("SELECT t.id, t.track_name FROM tracks t WHERE t.album_id=? AND (t.lyrics_text_path IS NULL OR t.lyrics_text_path='') AND (t.lyrics_lrc_path IS NULL OR t.lyrics_lrc_path='')", (aid,))
        tracks = c.fetchall()
        print(f"\n{art} - {alb} ({len(tracks)} tracks) [{co}]")
        
        for tid, tn in tracks:
            zh = co in ('中国','台湾','香港')
            lrc, txt = netease(art, tn) if zh else lrclib(art, tn)
            if not lrc and not txt:
                lrc, txt = lrclib(art, tn) if zh else netease(art, tn)
            
            if lrc or txt:
                lp, tp = save(art, alb, tn, lrc, txt)
                c.execute("UPDATE tracks SET lyrics_lrc_path=?, lyrics_text_path=? WHERE id=?", (lp, tp, tid))
                conn.commit()
                found += 1
                print(f"  OK: {tn}")
            else:
                missed += 1
            time.sleep(0.3)
    
    c.execute("SELECT COUNT(*) FROM tracks")
    tot = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM tracks WHERE (lyrics_text_path IS NOT NULL AND lyrics_text_path!='') OR (lyrics_lrc_path IS NOT NULL AND lyrics_lrc_path!='')")
    have = c.fetchone()[0]
    print(f"\nFound:{found} Missed:{missed} | {have}/{tot}={have/tot*100:.1f}% | Left:{tot-have}")
    conn.close()

if __name__ == '__main__':
    main()
