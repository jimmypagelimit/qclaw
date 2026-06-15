"""
批量歌词获取脚本
英文 → LRCLIB | 中文 → 网易云音乐
"""
import os, sys, time, json, sqlite3, urllib.request, urllib.parse, random
from datetime import datetime

# ========== 配置 ==========
DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
LYRICS_DIR = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics'
os.makedirs(LYRICS_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://music.163.com'
}

# ========== 网易云 ==========
def wangyiyun_search(query):
    """搜索网易云歌曲"""
    url = f'https://music.163.com/api/search/get?s={urllib.parse.quote(query)}&type=1&limit=5'
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        songs = data.get('result', {}).get('songs', [])
        if songs:
            return songs[0]['id'], songs[0].get('name', '')
    except Exception as e:
        pass
    return None, None

def wangyiyun_lyric(song_id):
    """获取网易云歌词（原文+翻译）"""
    url = f'https://music.163.com/api/song/lyric?id={song_id}&lv=1&tv=1'
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        lrc = data.get('lrc', {}).get('lyric', '')
        t_lrc = data.get('tlyric', {}).get('lyric', '')
        return lrc or '', t_lrc or ''
    except:
        return '', ''

# ========== LRCLIB ==========
def lrclib_search(artist, track):
    """搜索 LRCLIB"""
    q = f'{artist} {track}'
    url = f'https://lrclib.net/api/search?q={urllib.parse.quote(q)}'
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        resp = urllib.request.urlopen(req, timeout=10)
        results = json.loads(resp.read())
        if results:
            # 找最佳匹配
            best = min(results, key=lambda x: abs(x.get('duration', 0) - 999999))
            return best.get('syncedLyrics', ''), best.get('plainLyrics', '')
    except:
        pass
    return '', ''

# ========== 歌词保存 ==========
def save_lyrics(artist, album, tracks, source, lrc_text, plain_text, trans_lrc=''):
    """保存歌词到文件"""
    safe_artist = artist.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
    safe_album = album.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
    
    album_dir = os.path.join(LYRICS_DIR, f'{safe_artist} {safe_album}')
    os.makedirs(album_dir, exist_ok=True)
    
    saved = []
    for track_name, track_num in tracks:
        safe_track = track_name.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
        
        # 保存 LRC
        if lrc_text:
            lrc_path = os.path.join(album_dir, f'{track_num:02d}. {safe_track}.lrc')
            with open(lrc_path, 'w', encoding='utf-8') as f:
                f.write(lrc_text)
            saved.append(lrc_path)
        
        # 保存纯文本
        if plain_text:
            txt_path = os.path.join(album_dir, f'{track_num:02d}. {safe_track}.txt')
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(plain_text)
            saved.append(txt_path)
        
        # 保存翻译 LRC（网易云）
        if trans_lrc:
            zh_path = os.path.join(album_dir, f'{track_num:02d}. {safe_track}_zh.lrc')
            with open(zh_path, 'w', encoding='utf-8') as f:
                f.write(trans_lrc)
            saved.append(zh_path)
    
    return saved

# ========== 主流程 ==========
def get_tracks_from_db(album_id):
    """从数据库获取专辑曲目"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    
    # 获取专辑信息
    cur.execute("SELECT artist, album_name FROM albums WHERE album_id = ?", (album_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None, None, None
    artist, album = row
    
    # 获取曲目列表（从 MB 或网易云获取的曲目）
    # 这里简单处理：用专辑名+艺人搜索 MB 获取曲目
    conn.close()
    return artist, album, []

def is_chinese(text):
    """判断是否是中文歌曲"""
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    return chinese_chars > len(text) * 0.3

def process_album(album_id, limit=20):
    """处理单张专辑的歌词获取"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    
    # 获取专辑信息
    cur.execute("SELECT artist, album_name FROM albums WHERE album_id = ?", (album_id,))
    row = cur.fetchone()
    if not row:
        print(f'专辑不存在: {album_id}')
        conn.close()
        return 0
    artist, album = row
    
    # 检查是否已有歌词
    safe_artist = artist.replace('/', '_').replace('\\', '_')
    safe_album = album.replace('/', '_').replace('\\', '_')
    album_dir = os.path.join(LYRICS_DIR, f'{safe_artist} {safe_album}')
    
    if os.path.exists(album_dir):
        print(f'已有歌词目录: {album_dir}')
        # 检查文件数量
        existing = [f for f in os.listdir(album_dir) if f.endswith('.lrc')]
        if existing:
            print(f'  已有 {len(existing)} 个歌词文件，跳过')
            conn.close()
            return 0
    
    conn.close()
    
    # 获取曲目列表（使用 MusicBrainz 或手动曲目）
    tracks = get_tracks_from_db(album_id)
    
    print(f'处理: {artist} - {album} (album_id={album_id})')
    return 0

def main():
    """从数据库获取待处理专辑"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    
    # 获取所有专辑（按播放次数排序，取前N个未处理）
    cur.execute("""
        SELECT a.album_id, a.artist, a.album_name, 
               (SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id) as play_count
        FROM albums a
        WHERE a.album_name != ''
        ORDER BY play_count DESC
        LIMIT 20
    """)
    
    albums = cur.fetchall()
    conn.close()
    
    print(f'待处理专辑数量: {len(albums)}')
    
    # 先测试前3张
    for album_id, artist, album, play_count in albums[:3]:
        print(f'\n处理: {artist} - {album} (播放{play_count}次)')
        process_album(album_id)

if __name__ == '__main__':
    main()