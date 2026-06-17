#!/usr/bin/env python3
"""
网易云中文歌词批量获取 Phase 2
策略：搜索专辑ID → 获取专辑详情（含曲目列表）→ 逐首获取歌词

用法: python wy_batch.py --limit 3
      python wy_batch.py --album-id 85
"""

import os, sys, json, time, sqlite3, urllib.request, urllib.parse, re

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
LYRICS_DIR = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics'
DELAY = 1.0  # API 请求间隔（避免被封）

WY_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://music.163.com'
}
os.makedirs(LYRICS_DIR, exist_ok=True)

def safe(s):
    return ''.join(c for c in str(s) if c not in r'\/:*?"<>|').strip()

def has_chinese(s):
    return any('\u4e00' <= c <= '\u9fff' for c in s)

def fetch(url):
    req = urllib.request.Request(url, headers=WY_HEADERS)
    resp = urllib.request.urlopen(req, timeout=15)
    return json.loads(resp.read())

def search_album_id(artist, album):
    """搜索网易云专辑ID"""
    # 方式1：按专辑名搜索 (type=10)
    q = f'{artist} {album}'
    url = f'https://music.163.com/api/search/get?s={urllib.parse.quote(q)}&type=10&limit=10'
    try:
        data = fetch(url)
        albums = data.get('result', {}).get('albums', [])
        if albums:
            # 找最佳匹配：对照专辑名
            for al in albums:
                al_name = al.get('name', '')
                if album.lower() in al_name.lower() or al_name.lower() in album.lower():
                    return al['id'], al_name
            # 没完全匹配就取第一个
            return albums[0]['id'], albums[0].get('name', '')
    except Exception as e:
        pass
    
    # 方式2：按歌曲搜 (type=1)，从结果中找专辑
    q2 = f'{artist} {album}'
    url2 = f'https://music.163.com/api/search/get?s={urllib.parse.quote(q2)}&type=1&limit=10'
    try:
        data = fetch(url2)
        songs = data.get('result', {}).get('songs', [])
        seen = {}
        for s in songs:
            al = s.get('album', {}) if isinstance(s.get('album'), dict) else {}
            al_id = al.get('id', 0)
            al_name = al.get('name', '')
            if al_id and al_name:
                if album.lower() in al_name.lower() or al_name.lower() in album.lower():
                    seen[al_id] = al_name
        if seen:
            best_id = list(seen.keys())[0]
            return best_id, seen[best_id]
    except:
        pass
    return None, None

def get_album_tracks_via_search(artist, album_name):
    """通过歌曲搜索获取专辑曲目（绕过 -462 限制）"""
    q = f'{artist} {album_name}'
    url = f'https://music.163.com/api/search/get?s={urllib.parse.quote(q)}&type=1&limit=50'
    try:
        data = fetch(url)
        songs = data.get('result', {}).get('songs', [])
    except:
        return None
    
    tracks = []
    seen_ids = set()
    for s in songs:
        if s['id'] in seen_ids:
            continue
        seen_ids.add(s['id'])
        al = s.get('album', {}) or {}
        al_name = al.get('name', '') if isinstance(al, dict) else ''
        # 模糊匹配专辑名
        if (album_name.lower() in al_name.lower() or al_name.lower() in album_name.lower()):
            tracks.append({
                'id': s['id'],
                'name': s['name'],
                'position': len(tracks) + 1
            })
    
    if tracks:
        return tracks
    return None  # 标记为不可用

def get_album_tracks(album_id):
    """获取专辑所有曲目（尝试直接API，失败则改为搜索）"""
    url = f'https://music.163.com/api/album/{album_id}'
    try:
        data = fetch(url)
        if data.get('code') == 200:
            songs = data.get('album', {}).get('songs', [])
            if songs:
                return [{'id': s['id'], 'name': s['name'], 'position': s.get('no', i+1)} for i, s in enumerate(songs)]
        # code != 200 或空 → 改用搜索
        return None
    except:
        return None

def get_lyric(song_id):
    """获取歌词 + 翻译"""
    url = f'https://music.163.com/api/song/lyric?id={song_id}&lv=1&tv=1'
    data = fetch(url)
    lrc = data.get('lrc', {}).get('lyric', '') or ''
    t_lrc = data.get('tlyric', {}).get('lyric', '') or ''
    return lrc, t_lrc

def parse_lrc_to_text(lrc_text):
    """LRC格式 → 纯文本（去掉时间戳）"""
    lines = []
    for line in lrc_text.split('\n'):
        # 去掉 [mm:ss.xx] 时间戳
        clean = re.sub(r'\[\d+:\d+\.\d+\]', '', line).strip()
        if clean and not clean.startswith('['):
            lines.append(clean)
    return '\n'.join(lines)

def make_bilingual(lrc_text, trans_text):
    """按时间戳对齐原歌词+翻译"""
    lrc_re = re.compile(r'\[(\d+:\d+\.\d+)\](.*)')
    
    orig_lines = {}
    for line in lrc_text.split('\n'):
        m = lrc_re.match(line)
        if m:
            ts, text = m.group(1), m.group(2).strip()
            if text:
                orig_lines[ts] = text
    
    trans_lines = {}
    for line in trans_text.split('\n'):
        m = lrc_re.match(line)
        if m:
            ts, text = m.group(1), m.group(2).strip()
            if text:
                trans_lines[ts] = text
    
    result = []
    for ts in sorted(orig_lines.keys()):
        orig = orig_lines[ts]
        trans = trans_lines.get(ts, '')
        if trans:
            result.append(f'{orig} / {trans}')
            del trans_lines[ts]
        else:
            result.append(orig)
    
    # 多余的翻译
    for ts in sorted(trans_lines.keys()):
        result.append(f'[翻译] {trans_lines[ts]}')
    
    return '\n'.join(result)

def process_album(artist, album_name):
    """处理一张中文专辑"""
    save_dir = os.path.join(LYRICS_DIR, safe(artist), safe(album_name))
    
    # 跳过已有
    if os.path.exists(save_dir):
        existing = [f for f in os.listdir(save_dir) if f.endswith('.lrc')]
        if existing:
            print(f'  跳过：已有 {len(existing)} 个 LRC')
            return {'skip': True, 'count': len(existing)}
    
    os.makedirs(save_dir, exist_ok=True)
    
    # 搜索专辑
    print(f'  搜索网易云专辑...')
    al_id, al_name = search_album_id(artist, album_name)
    if not al_id:
        print(f'  无法找到专辑')
        return {'fail': 1}
    
    print(f'  找到专辑: {al_name} (id={al_id})')
    time.sleep(DELAY)
    
    # 获取曲目
    print(f'  获取曲目列表...')
    tracks = get_album_tracks(al_id)
    if not tracks:
        print(f'  专辑API不可用，改用歌曲搜索...')
        tracks = get_album_tracks_via_search(artist, album_name)
    
    if not tracks:
        print(f'  无法获取曲目（可能此专辑不在网易云）')
        return {'fail': 1}
    
    print(f'  曲目: {len(tracks)} 首')
    time.sleep(DELAY)
    
    # 获取每首歌词
    ok = fail = 0
    for t in tracks:
        lrc, trans = get_lyric(t['id'])
        num = t['position']
        title = t['name']
        fname = f'{num:02d}. {safe(title)}'
        
        if lrc:
            # 保存 LRC
            with open(os.path.join(save_dir, f'{fname}.lrc'), 'w', encoding='utf-8') as f:
                f.write(lrc)
            # 保存纯文本
            plain = parse_lrc_to_text(lrc)
            if plain:
                with open(os.path.join(save_dir, f'{fname}.txt'), 'w', encoding='utf-8') as f:
                    f.write(plain)
            ok += 1
            status = 'WY lrc+txt'
            
            # 翻译
            if trans:
                with open(os.path.join(save_dir, f'{fname}_zh.lrc'), 'w', encoding='utf-8') as f:
                    f.write(trans)
                status += '+trans'
                # 双语
                bilingual = make_bilingual(lrc, trans)
                if bilingual:
                    with open(os.path.join(save_dir, f'{fname}_bilingual.txt'), 'w', encoding='utf-8') as f:
                        f.write(bilingual)
                    status += '+bilingual'
        else:
            fail += 1
            status = 'NO LYRIC'
        
        try:
            print(f'    {num:2d}. {title[:30]:30s} [{status}]')
        except UnicodeEncodeError:
            safe_title = title.encode('ascii', 'replace').decode('ascii')
            print(f'    {num:2d}. {safe_title[:30]:30s} [{status}]')
        time.sleep(DELAY + 0.5)  # 歌词API间隔稍长
    
    return {'ok': ok, 'fail': fail, 'total': len(tracks)}

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=5, help='处理前N张中文专辑')
    parser.add_argument('--album-id', type=int, help='指定album_id处理')
    args = parser.parse_args()
    
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    
    if args.album_id:
        cur.execute("SELECT album_id, artist, album_name FROM albums WHERE album_id = ?", (args.album_id,))
        rows = cur.fetchall()
    else:
        # 按收听次数排序，只选中文专辑
        cur.execute("""
            SELECT a.album_id, a.artist, a.album_name,
                   (SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id) as pc
            FROM albums a
            WHERE a.album_name != ''
            ORDER BY pc DESC
        """)
        rows = cur.fetchall()
    conn.close()
    
    # 过滤出中文的
    candidates = [(r[0], r[1], r[2]) for r in rows if has_chinese(str(r[1])) or has_chinese(str(r[2]))]
    
    # 去重检查
    to_process = []
    for a_id, art, alb in candidates:
        save_dir = os.path.join(LYRICS_DIR, safe(art), safe(alb))
        if not os.path.exists(save_dir) or not any(f.endswith('.lrc') for f in os.listdir(save_dir)):
            to_process.append((a_id, art, alb))
    
    if args.album_id:
        to_process = [(r[0], r[1], r[2]) for r in rows if has_chinese(str(r[1])) or has_chinese(str(r[2]))]
    
    to_process = to_process[:args.limit]
    
    print(f'待处理中文专辑: {len(to_process)} 张\n')
    
    total_ok = total_fail = 0
    for a_id, art, alb in to_process:
        print(f'=== {art} - {alb} (id={a_id}) ===')
        result = process_album(art, alb)
        if 'skip' not in result:
            total_ok += result.get('ok', 0)
            total_fail += result.get('fail', 0)
        print()
    
    print(f'完成: OK={total_ok} FAIL={total_fail}')

if __name__ == '__main__':
    main()
