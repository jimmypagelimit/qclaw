#!/usr/bin/env python3
"""
MusicBrainz 曲目表获取 v3
策略：全部走 curl（Python SSL 间歇性全挂）
"""
import subprocess, json, sys, os, time, urllib.parse

BASE = "https://musicbrainz.org/ws/2"
UA = "AlbumTracker/1.0 (jim@example.com)"

def mb_curl(url, timeout=20):
    """用 curl 获取 MusicBrainz JSON"""
    try:
        result = subprocess.run(
            ['curl', '-s', '--connect-timeout', '10',
             '-H', f'User-Agent: {UA}', url],
            capture_output=True, text=True, timeout=timeout
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
        else:
            print(f"    curl rc={result.returncode}: {result.stderr[:200]}")
            return None
    except subprocess.TimeoutExpired:
        print("    curl 超时")
        return None
    except json.JSONDecodeError as e:
        print(f"    JSON 解析失败: {e}")
        return None

def mb_search(entity, query, limit=5):
    """搜索"""
    params = urllib.parse.urlencode({'query': query, 'fmt': 'json', 'limit': limit})
    url = f"{BASE}/{entity}/?{params}"
    return mb_curl(url)

def mb_lookup(path):
    """Lookup"""
    url = f"{BASE}/{path}"
    return mb_curl(url)

def get_tracklist(artist, album):
    """获取专辑曲目列表"""
    # Step 1: 搜索 release-group
    print(f"[1] 搜索 release-group: {artist} - {album}")
    data = mb_search('release-group', f'{album} AND artist:{artist}', limit=10)
    
    if not data:
        print("    搜索失败")
        return None
    
    rgs = data.get('release-groups', [])
    if not rgs:
        print("    无结果")
        return None
    
    # 选最佳匹配
    best = None
    for rg in rgs:
        score = rg.get('score', 0)
        ptype = rg.get('primary-type', '')
        stypes = rg.get('secondary-types', [])
        # 优先 Album + 非Demo/非Remix + score 高
        if ptype == 'Album' and 'Demo' not in stypes and 'Remix' not in stypes:
            if best is None or score > best.get('score', 0):
                best = rg
    
    if not best:
        best = rgs[0]
    
    rg_id = best['id']
    print(f"    选择: {best['title']} (score={best.get('score')}, ID={rg_id[:12]}...)")
    
    # Step 2: 获取 release ID
    releases = best.get('releases', [])
    if releases:
        for r in releases:
            if r.get('status') == 'Official':
                rel_id = r['id']
                break
        else:
            rel_id = releases[0]['id']
    else:
        print("    需 lookup 获取 releases...")
        time.sleep(1)
        rg_data = mb_lookup(f"release-group/{rg_id}?inc=releases&fmt=json")
        if rg_data and rg_data.get('releases'):
            rel_id = rg_data['releases'][0]['id']
        else:
            print("    无法获取 release ID")
            return None
    
    print(f"    Release ID: {rel_id[:12]}...")
    
    # Step 3: 获取曲目列表
    print(f"[2] 获取曲目列表...")
    time.sleep(1)
    rel_data = mb_lookup(f"release/{rel_id}?inc=recordings&fmt=json")
    
    if not rel_data:
        print("    获取曲目失败")
        return None
    
    tracks = []
    for m in rel_data.get('media', []):
        fmt = m.get('format', '')
        for t in m.get('tracks', []):
            tracks.append({
                'position': t.get('position', 0),
                'title': t.get('title', ''),
                'duration_ms': t.get('length', 0),
                'recording_id': t.get('recording', {}).get('id', ''),
                'format': fmt,
            })
    
    print(f"    共 {len(tracks)} 首曲目:")
    for t in tracks:
        dur = f"{t['duration_ms']//1000}s" if t['duration_ms'] else "?"
        print(f"      {t['position']:2d}. {t['title']} ({dur})")
    
    return tracks

# ===== 主逻辑 =====
if __name__ == '__main__':
    if len(sys.argv) >= 3:
        artist = sys.argv[1]
        album = " ".join(sys.argv[2:])
    else:
        artist = input("艺人: ").strip()
        album = input("专辑: ").strip()
    
    tracks = get_tracklist(artist, album)
    
    if tracks:
        out_dir = os.path.join(os.path.dirname(__file__), "tracklists")
        os.makedirs(out_dir, exist_ok=True)
        safe_name = "".join(c for c in f"{artist}-{album}" if c not in r'\\/:*?"<>|')
        out_path = os.path.join(out_dir, f"{safe_name}.json")
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump({'artist': artist, 'album': album, 'tracks': tracks}, f, ensure_ascii=False, indent=2)
        print(f"\n曲目列表已保存: {out_path}")
