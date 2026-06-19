#!/usr/bin/env python3
"""
封面下载模块 - 优先级：CAA > 网易云 > iTunes > Deezer
新增专辑时调用此模块，已有封面不替换

用法:
    from cover_download import download_cover_for_album
    success, msg = download_cover_for_album(album_id, artist, album_name, mbid)
"""

import sqlite3
import urllib.request
import urllib.parse
import ssl
import os
import json
import time

# ── 配置 ──────────────────────────────────────────────────────────────────────
DB_PATH   = 'C:/Users/qujt/.qclaw/workspace/_music_latest.db'
COVER_DIR = 'C:/Users/qujt/.qclaw/workspace/tasks/2026-05-12-long-term-project/album-tracker/public/covers'
SSL_CTX   = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE
PAUSE     = 0.5   # 请求间隔（秒）
# ────────────────────────────────────────────────────────────────────────────────


def safe_filename(artist, album, album_id):
    """生成安全文件名"""
    base = f"{artist}-{album}".replace('/', '_').replace('\\', '_')[:60]
    return f"{album_id}-{base}.jpg"


def download_caa(mbid, out_path):
    """尝试从 Cover Art Archive 下载"""
    url = f"https://coverartarchive.org/release/{mbid}/front"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'album-tracker/1.0'})
        resp = urllib.request.urlopen(req, timeout=15, context=SSL_CTX)
        if resp.status == 200:
            data = resp.read()
            with open(out_path, 'wb') as f:
                f.write(data)
            return True, f"{len(data)/1024:.0f}KB"
    except Exception as e:
        pass
    return False, None


def download_netease(artist, album, out_path):
    """尝试从网易云 API 下载"""
    try:
        # 搜索专辑
        keyword = urllib.parse.quote(f"{artist} {album}")
        search_url = f"https://music.163.com/api/search/get?s={keyword}&type=10&limit=1&offset=0"
        req = urllib.request.Request(search_url, headers={
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://music.163.com/'
        })
        resp = urllib.request.urlopen(req, timeout=10, context=SSL_CTX)
        data = json.loads(resp.read())
        if data.get('result', {}).get('albums'):
            album_info = data['result']['albums'][0]
            pic_url = album_info.get('picUrl', '').replace('http://', 'https://')
            if pic_url:
                req2 = urllib.request.Request(pic_url, headers={'User-Agent': 'Mozilla/5.0'})
                resp2 = urllib.request.urlopen(req2, timeout=10, context=SSL_CTX)
                img_data = resp2.read()
                with open(out_path, 'wb') as f:
                    f.write(img_data)
                return True, f"{len(img_data)/1024:.0f}KB"
    except Exception as e:
        pass
    return False, None


def download_itunes(artist, album, out_path):
    """尝试从 iTunes API 下载"""
    try:
        keyword = urllib.parse.quote(f"{artist} {album}")
        search_url = f"https://itunes.apple.com/search?term={keyword}&entity=album&limit=1"
        req = urllib.request.Request(search_url, headers={'User-Agent': 'album-tracker/1.0'})
        resp = urllib.request.urlopen(req, timeout=10, context=SSL_CTX)
        data = json.loads(resp.read())
        if data.get('results'):
            art_url = data['results'][0].get('artworkUrl100', '').replace('100x100bb', '600x600bb')
            if art_url:
                req2 = urllib.request.Request(art_url, headers={'User-Agent': 'album-tracker/1.0'})
                resp2 = urllib.request.urlopen(req2, timeout=10, context=SSL_CTX)
                img_data = resp2.read()
                with open(out_path, 'wb') as f:
                    f.write(img_data)
                return True, f"{len(img_data)/1024:.0f}KB"
    except Exception as e:
        pass
    return False, None


def download_deezer(artist, album, out_path):
    """尝试从 Deezer API 下载"""
    try:
        keyword = urllib.parse.quote(f"{artist} {album}")
        search_url = f"https://api.deezer.com/search/album?q={keyword}&limit=1"
        req = urllib.request.Request(search_url, headers={'User-Agent': 'album-tracker/1.0'})
        resp = urllib.request.urlopen(req, timeout=10, context=SSL_CTX)
        data = json.loads(resp.read())
        if data.get('data'):
            cover_url = data['data'][0].get('cover_big', '').replace('http://', 'https://')
            if cover_url:
                req2 = urllib.request.Request(cover_url, headers={'User-Agent': 'album-tracker/1.0'})
                resp2 = urllib.request.urlopen(req2, timeout=10, context=SSL_CTX)
                img_data = resp2.read()
                with open(out_path, 'wb') as f:
                    f.write(img_data)
                return True, f"{len(img_data)/1024:.0f}KB"
    except Exception as e:
        pass
    return False, None


def download_cover_for_album(album_id, artist, album_name, mbid=None):
    """
    为专辑下载封面，按优先级：CAA > 网易云 > iTunes > Deezer
    返回 (success: bool, message: str)
    """
    os.makedirs(COVER_DIR, exist_ok=True)
    fname = safe_filename(artist, album_name, album_id)
    fpath = os.path.join(COVER_DIR, fname)

    # 已有封面文件则跳过
    if os.path.exists(fpath):
        return False, "SKIP (文件已存在)"

    sources = []

    # 优先级1：CAA（需要 MBID）
    if mbid and mbid.strip():
        mbid_clean = mbid.strip().strip('{}')
        sources.append(('CAA', lambda: download_caa(mbid_clean, fpath)))

    # 优先级2：网易云
    sources.append(('网易云', lambda: download_netease(artist, album_name, fpath)))

    # 优先级3：iTunes
    sources.append(('iTunes', lambda: download_itunes(artist, album_name, fpath)))

    # 优先级4：Deezer
    sources.append(('Deezer', lambda: download_deezer(artist, album_name, fpath)))

    for source_name, download_func in sources:
        try:
            success, info = download_func()
            if success:
                # 更新数据库
                rel_path = f"/covers/{fname}"
                conn = sqlite3.connect(DB_PATH)
                conn.execute('PRAGMA journal_mode=WAL')
                conn.execute("UPDATE albums SET cover_image_url = ? WHERE album_id = ?", (rel_path, album_id))
                conn.commit()
                conn.close()
                return True, f"OK ({source_name}) {info}"
        except Exception as e:
            continue
        time.sleep(PAUSE)

    return False, "FAIL (所有源均失败)"


# ── 命令行测试 ─────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    import sys
    if len(sys.argv) >= 4:
        aid   = int(sys.argv[1])
        art   = sys.argv[2]
        alb   = sys.argv[3]
        mbid  = sys.argv[4] if len(sys.argv) > 4 else None
        ok, msg = download_cover_for_album(aid, art, alb, mbid)
        print(f"{'✓' if ok else '✗'} {msg}  {art} - {alb}")
    else:
        print("用法: python cover_download.py <album_id> <artist> <album> [mbid]")
        print("示例: python cover_download.py 1 'Car Seat Headrest' 'Twin Fantasy' 'fad66642-c055-...'")
