#!/usr/bin/env python3
"""
L 项目 - 歌词获取管道 v1
流程：MusicBrainz(曲目表) → LRCLIB(歌词) → 本地保存

当前状态：
- MusicBrainz: 间歇性不可用（Windows SSL 问题），搜索 API 偶尔能通
- LRCLIB: 英文歌词正常，中文无数据
- 中文歌词需走 Lyricstranslate.com（待实现）

用法：
  python lyrics_pipeline.py "Car Seat Headrest" "Twin Fantasy"
  python lyrics_pipeline.py  # 交互模式
"""
import subprocess, json, sys, os, time, urllib.parse, urllib.request

# ===== 配置 =====
MB_BASE = "https://musicbrainz.org/ws/2"
LRCLIB_BASE = "https://lrclib.net/api"
UA = "AlbumTracker/1.0 (jim@example.com)"
LYRICS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lyrics")
TRACKLISTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tracklists")

os.makedirs(LYRICS_DIR, exist_ok=True)
os.makedirs(TRACKLISTS_DIR, exist_ok=True)

# ===== MusicBrainz =====

def mb_request(url, timeout=20):
    """MusicBrainz 请求：先 curl，失败则 Python urllib"""
    # 尝试 curl
    try:
        result = subprocess.run(
            ['curl', '-s', '--connect-timeout', '10', '--max-time', str(timeout),
             '-H', f'User-Agent: {UA}', url],
            capture_output=True, text=True, timeout=timeout + 5
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
    except Exception:
        pass
    
    # 尝试 Python urllib
    try:
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return json.loads(resp.read())
    except Exception:
        pass
    
    return None

def mb_search_release_group(artist, album):
    """搜索 release-group"""
    query = f'{album} AND artist:{artist}'
    params = urllib.parse.urlencode({'query': query, 'fmt': 'json', 'limit': 10})
    url = f"{MB_BASE}/release-group/?{params}"
    return mb_request(url)

def mb_get_tracklist(release_id):
    """获取 release 的曲目列表"""
    url = f"{MB_BASE}/release/{release_id}?inc=recordings&fmt=json"
    return mb_request(url)

# ===== LRCLIB =====

def lrclib_search(artist, track, timeout=15):
    """搜索歌词"""
    params = urllib.parse.urlencode({'q': f'{artist} {track}'})
    url = f"{LRCLIB_BASE}/search?{params}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"    LRCLIB 搜索失败: {e}")
        return []

def lrclib_get(lrc_id, timeout=15):
    """按 ID 获取完整歌词"""
    url = f"{LRCLIB_BASE}/get/{lrc_id}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"    LRCLIB 获取失败: {e}")
        return None

# ===== 保存 =====

def save_lyrics(artist, album, track_name, lrc_text, plain_text):
    """保存歌词文件"""
    safe_artist = "".join(c for c in artist if c not in r'\\/:*?"<>|').strip()
    safe_album = "".join(c for c in album if c not in r'\\/:*?"<>|').strip()
    safe_track = "".join(c for c in track_name if c not in r'\\/:*?"<>|').strip()
    
    base = os.path.join(LYRICS_DIR, safe_artist, safe_album)
    os.makedirs(base, exist_ok=True)
    
    saved = []
    if lrc_text:
        path = os.path.join(base, f"{safe_track}.lrc")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(lrc_text)
        saved.append(path)
    
    if plain_text:
        path = os.path.join(base, f"{safe_track}.txt")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(plain_text)
        saved.append(path)
    
    return saved

# ===== 主管道 =====

def process_album(artist, album):
    """处理一张专辑：获取曲目 → 逐首搜歌词 → 保存"""
    print(f"\n{'='*50}")
    print(f"专辑: {artist} - {album}")
    print(f"{'='*50}")
    
    # Step 1: 搜索 release-group
    print("\n[1] MusicBrainz: 搜索 release-group...")
    data = mb_search_release_group(artist, album)
    
    if not data or not data.get('release-groups'):
        print("    ❌ 搜索失败或无结果（MusicBrainz 可能不可用）")
        print("    提示：可手动创建曲目列表 JSON 到 tracklists/ 目录")
        return None
    
    rgs = data['release-groups']
    print(f"    命中 {len(rgs)} 个 release-group")
    
    # 选最佳匹配
    best = None
    for rg in rgs:
        ptype = rg.get('primary-type', '')
        stypes = rg.get('secondary-types', [])
        if ptype == 'Album' and 'Demo' not in stypes and 'Remix' not in stypes:
            if best is None or rg.get('score', 0) > best.get('score', 0):
                best = rg
    if not best:
        best = rgs[0]
    
    rg_id = best['id']
    print(f"    选择: {best['title']} (score={best.get('score')})")
    
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
        rg_data = mb_request(f"{MB_BASE}/release-group/{rg_id}?inc=releases&fmt=json")
        if rg_data and rg_data.get('releases'):
            rel_id = rg_data['releases'][0]['id']
        else:
            print("    ❌ 无法获取 release ID")
            return None
    
    print(f"    Release ID: {rel_id[:12]}...")
    
    # Step 3: 获取曲目列表
    print("\n[2] MusicBrainz: 获取曲目列表...")
    time.sleep(1)
    rel_data = mb_get_tracklist(rel_id)
    
    if not rel_data:
        print("    ❌ 获取曲目列表失败")
        return None
    
    tracks = []
    for m in rel_data.get('media', []):
        for t in m.get('tracks', []):
            tracks.append({
                'position': t.get('position', 0),
                'title': t.get('title', ''),
                'duration_ms': t.get('length', 0),
            })
    
    print(f"    共 {len(tracks)} 首:")
    for t in tracks:
        dur = f"{t['duration_ms']//1000}s" if t['duration_ms'] else "?"
        print(f"      {t['position']:2d}. {t['title']} ({dur})")
    
    # 保存曲目列表
    safe_name = "".join(c for c in f"{artist}-{album}" if c not in r'\\/:*?"<>|')
    tl_path = os.path.join(TRACKLISTS_DIR, f"{safe_name}.json")
    with open(tl_path, 'w', encoding='utf-8') as f:
        json.dump({'artist': artist, 'album': album, 'tracks': tracks, 'release_id': rel_id}, f, ensure_ascii=False, indent=2)
    print(f"    曲目列表已保存: {tl_path}")
    
    # Step 4: 逐首搜歌词
    print(f"\n[3] LRCLIB: 获取歌词...")
    ok = 0
    fail = 0
    no_lyrics = 0
    
    for t in tracks:
        title = t['title']
        print(f"  [{t['position']:2d}] {title}")
        
        try:
            results = lrclib_search(artist, title)
            if not results:
                print(f"      ❌ 无结果")
                no_lyrics += 1
                time.sleep(1)
                continue
            
            # 取第一个匹配
            first = results[0]
            lrc_id = first['id']
            
            # 获取完整歌词
            full = lrclib_get(lrc_id)
            if not full:
                fail += 1
                time.sleep(1)
                continue
            
            lrc_text = full.get('syncedLyrics', '')
            plain_text = full.get('plainLyrics', '')
            
            if not lrc_text and not plain_text:
                print(f"      ❌ 无歌词内容")
                no_lyrics += 1
                time.sleep(1)
                continue
            
            saved = save_lyrics(artist, album, title, lrc_text, plain_text)
            print(f"      ✅ 保存 {len(saved)} 个文件")
            ok += 1
            
        except Exception as e:
            print(f"      ❌ 错误: {e}")
            fail += 1
        
        time.sleep(1)  # LRCLIB 限速
    
    print(f"\n{'='*50}")
    print(f"结果：✅ {ok} 首 | ❌ {fail} 首失败 | ⚪ {no_lyrics} 首无歌词 | 共 {len(tracks)} 首")
    print(f"{'='*50}")
    
    return {'ok': ok, 'fail': fail, 'no_lyrics': no_lyrics, 'total': len(tracks)}

# ===== 入口 =====

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        artist = sys.argv[1]
        album = " ".join(sys.argv[2:])
    else:
        artist = input("艺人: ").strip()
        album = input("专辑: ").strip()
    
    if not artist or not album:
        print("需要艺人名和专辑名")
        sys.exit(1)
    
    result = process_album(artist, album)
