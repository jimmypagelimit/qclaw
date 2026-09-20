#!/usr/bin/env python3
"""
L项目歌词补齐管道 v2（Linux 适配）
英文 -> LRCLIB ；中文 -> 网易云
保存 Artist/Album/NN. Track.lrc + .txt，更新数据库相对路径
"""
import os, sys, json, time, re, socket, sqlite3, urllib.request, urllib.parse
socket.setdefaulttimeout(8)

DB = '/root/qclaw/tasks/2026-05-12-long-term-project/album-tracker/music'
ROOT = '/root/qclaw/tasks/lyrics-expert/lyrics'

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
WY_HEADERS = {'User-Agent': UA, 'Referer': 'https://music.163.com'}

def has_cn(s):
    return bool(re.search(r'[\u4e00-\u9fff]', s))

def safe(s):
    return re.sub(r'[\\/:*?"<>|]', '_', s)

def http_json(url, headers=None, timeout=8, tries=3):
    import socket as _socket
    _socket.setdefaulttimeout(timeout)
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=headers or {'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode('utf-8', 'ignore'))
        except Exception:
            if i == tries - 1:
                return None
            time.sleep(1.5 * (i + 1))
    return None

def lrclib(track, artist):
    q = urllib.parse.quote(f'{artist} {track}')
    data = http_json(f'https://lrclib.net/api/search?q={q}')
    if not data:
        return None
    for item in data:
        t = (item.get('albumName') or '').lower()
        a = (item.get('artistName') or '').lower()
        if a and artist.lower() in a and (item.get('trackName') or '').lower() == track.lower():
            syn = item.get('syncedLyrics') or ''
            plain = item.get('plainLyrics') or ''
            if syn or plain:
                return {'lrc': syn or _lrc_from_plain(plain), 'txt': plain}
    return None

def _lrc_from_plain(plain):
    return plain

def wangyiyun(track, artist, album=''):
    query = f'{track} {artist}'.strip()
    url = f'http://music.163.com/api/search/get?s={urllib.parse.quote(query)}&type=1&limit=5'
    data = http_json(url, WY_HEADERS)
    if not data:
        return None
    songs = data.get('result', {}).get('songs', [])
    sid = None
    for s in songs:
        sname = s.get('name', '')
        sart = (s.get('artists') or [{}])[0].get('name', '') if s.get('artists') else (s.get('artist') or [''])[0]
        if sname and sname.lower() == track.lower():
            sid = s['id']
            break
    if not sid and songs:
        sid = songs[0]['id']
    if not sid:
        return None
    ldata = http_json(f'http://music.163.com/api/song/lyric?id={sid}&lv=1&tv=1', WY_HEADERS)
    if not ldata:
        return None
    lrc = (ldata.get('lrc') or {}).get('lyric', '') or ''
    tlrc = (ldata.get('tlyric') or {}).get('lyric', '') or ''
    if not lrc:
        return None
    plain = '\n'.join(line.split(']')[-1].strip() for line in lrc.splitlines() if line.strip())
    return {'lrc': lrc, 'txt': plain, 'trans': tlrc}

def process_album(album_id, limit=None):
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    album = cur.execute('SELECT album_id, artist, album_name FROM albums WHERE album_id=?', (album_id,)).fetchone()
    if not album:
        print(f'  [x] album {album_id} not found')
        return 0, 0
    tracks = cur.execute("""
        SELECT id, track_number, track_name FROM tracks
        WHERE album_id=? AND (lyrics_lrc_path IS NULL OR lyrics_lrc_path='')
        ORDER BY track_number, id
    """, (album_id,)).fetchall()
    if limit:
        tracks = tracks[:limit]
    artist, album_name = album['artist'], album['album_name']
    print(f'== {artist} - {album_name} ({len(tracks)} missing)')
    cn = has_cn(artist) or has_cn(album_name)
    ok = 0
    for t in tracks:
        track = t['track_name'].strip().strip('"\'“”')
        num = t['track_number']
        src = '网易云' if cn else 'LRCLIB'
        res = wangyiyun(track, artist, album_name) if cn else lrclib(track, artist)
        if not res:
            print(f'  -  miss [{num}] {track}')
            time.sleep(0.4)
            continue
        artist_dir = os.path.join(ROOT, safe(artist))
        album_dir = os.path.join(artist_dir, safe(album_name))
        os.makedirs(album_dir, exist_ok=True)
        fname = f'{num:02d}. {safe(track)}' if num else safe(track)
        # 同专辑同名曲目（demo/bootleg）可能重复，加 id 后缀防止覆盖
        clash = cur.execute(
            'SELECT COUNT(*) FROM tracks WHERE album_id=? AND lyrics_lrc_path LIKE ?',
            (album_id, f'%{fname}%')
        ).fetchone()[0]
        if clash:
            fname = f'{fname} [{t["id"]}]'
        lrc_path = os.path.join(album_dir, fname + '.lrc')
        txt_path = os.path.join(album_dir, fname + '.txt')
        with open(lrc_path, 'w', encoding='utf-8') as f:
            f.write(res['lrc'])
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(res['txt'])
        # 数据库存相对路径
        rel_lrc = os.path.relpath(lrc_path, ROOT)
        rel_txt = os.path.relpath(txt_path, ROOT)
        cur.execute('UPDATE tracks SET lyrics_lrc_path=?, lyrics_text_path=? WHERE id=?', (rel_lrc, rel_txt, t['id']))
        conn.commit()
        ok += 1
        print(f'  +  ok   [{num}] {track} ({len(res["lrc"])}ch)')
        time.sleep(0.4)
    conn.close()
    return ok, len(tracks)

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--album', type=int, action='append', default=[])
    ap.add_argument('--top', type=int, default=0, help='处理缺失最多的N张专辑')
    args = ap.parse_args()
    if args.album:
        for aid in args.album:
            ok, total = process_album(aid)
            print(f'  -> {ok}/{total}')
    elif args.top:
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        rows = cur.execute("""
            SELECT t.album_id FROM tracks t
            WHERE (t.lyrics_lrc_path IS NULL OR t.lyrics_lrc_path='')
            GROUP BY t.album_id ORDER BY COUNT(*) DESC LIMIT ?
        """, (args.top,)).fetchall()
        conn.close()
        for (aid,) in rows:
            ok, total = process_album(aid)
            print(f'  -> {ok}/{total}')