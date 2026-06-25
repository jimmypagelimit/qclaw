"""
Cron任务：推进歌词计划
从数据库获取待处理的中文专辑，使用网易云API批量获取歌词
"""
import os
import sys
import json
import time
import sqlite3
import urllib.request
import urllib.parse
from datetime import datetime

# 配置
DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
LYRICS_DIR = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics'
LOG_FILE = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\cron_log.txt'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://music.163.com'
}

def log(msg):
    """写入日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{timestamp}] {msg}'
    print(line)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def wangyiyun_search(song_name, artist=''):
    """搜索网易云歌曲，返回歌曲ID"""
    query = f'{song_name} {artist}'.strip()
    url = f'https://music.163.com/api/search/get?s={urllib.parse.quote(query)}&type=1&limit=3'
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        songs = data.get('result', {}).get('songs', [])
        if songs:
            return songs[0]['id'], songs[0].get('name', '')
    except Exception as e:
        log(f'  搜索失败: {song_name} - {e}')
    return None, None

def wangyiyun_lyric(song_id):
    """获取网易云歌词（原文+翻译）"""
    url = f'https://music.163.com/api/song/lyric?id={song_id}&lv=1&tv=1'
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        lrc = data.get('lrc', {}).get('lyric', '')
        tlyric = data.get('tlyric', {}).get('lyric', '')
        return lrc or '', tlyric or ''
    except Exception as e:
        log(f'  获取歌词失败: {song_id} - {e}')
    return '', ''

def save_lyrics(artist, album, track_name, track_num, lrc_text, trans_text=''):
    """保存歌词到文件"""
    safe_artist = artist.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
    safe_album = album.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
    safe_track = track_name.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
    
    album_dir = os.path.join(LYRICS_DIR, safe_artist, safe_album)
    os.makedirs(album_dir, exist_ok=True)
    
    saved = []
    
    # 保存LRC
    if lrc_text:
        lrc_path = os.path.join(album_dir, f'{track_num:02d}. {safe_track}.lrc')
        with open(lrc_path, 'w', encoding='utf-8') as f:
            f.write(lrc_text)
        saved.append(lrc_path)
    
    # 保存纯文本
    if lrc_text:
        # 简单去除LRC时间戳
        lines = [line.split(']')[-1] if ']' in line else line for line in lrc_text.split('\n')]
        plain_text = '\n'.join(lines)
        txt_path = os.path.join(album_dir, f'{track_num:02d}. {safe_track}.txt')
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(plain_text)
        saved.append(txt_path)
    
    # 保存翻译
    if trans_text:
        trans_path = os.path.join(album_dir, f'{track_num:02d}. {safe_track}_trans.txt')
        with open(trans_path, 'w', encoding='utf-8') as f:
            f.write(trans_text)
        saved.append(trans_path)
    
    return saved

def get_album_tracks_from_db(album_id):
    """从数据库获取专辑的曲目列表（这里需要从某个来源获取曲目）"""
    # 注意：当前数据库可能没有完整的曲目列表
    # 这里返回一个空列表，表示需要手动搜索
    return []

def is_chinese(text):
    """判断是否是中文"""
    if not text:
        return False
    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    return chinese_chars > len(text) * 0.2

def process_album(album_id, conn):
    """处理单张专辑"""
    cur = conn.cursor()
    
    # 获取专辑信息
    cur.execute("SELECT artist, album_name FROM albums WHERE album_id = ?", (album_id,))
    row = cur.fetchone()
    if not row:
        return 0
    
    artist, album = row
    
    # 检查是否已有歌词
    safe_artist = artist.replace('/', '_').replace('\\', '_')
    safe_album = album.replace('/', '_').replace('\\', '_')
    album_dir = os.path.join(LYRICS_DIR, safe_artist, safe_album)
    
    if os.path.exists(album_dir):
        existing = [f for f in os.listdir(album_dir) if f.endswith('.lrc')]
        if len(existing) >= 3:  # 至少有3首歌的歌词
            log(f'跳过（已有{len(existing)}个歌词）: {artist} - {album}')
            return 0
    
    log(f'处理: {artist} - {album}')
    
    # 获取专辑的曲目（这里需要先从某个来源获取曲目列表）
    # 由于没有曲目列表，我们直接搜索专辑中的歌曲
    # 这里假设我们有一个曲目列表的来源
    
    # 简单处理：搜索专辑名+艺人名，获取热门歌曲
    # 这是一个简化实现，实际需要完整的曲目列表
    
    log(f'  需要曲目列表，跳过')
    return 0

def get_pending_albums(limit=10):
    """获取待处理的中文专辑列表"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    
    # 获取所有中文专辑（简单判断：专辑名或艺人名包含中文字符）
    cur.execute("""
        SELECT a.album_id, a.artist, a.album_name,
               (SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id) as play_count
        FROM albums a
        WHERE a.album_name != '' 
          AND (a.album_name GLOB '*[一-龥]*' OR a.artist GLOB '*[一-龥]*')
        ORDER BY play_count DESC
    """)
    
    albums = cur.fetchall()
    conn.close()
    
    # 过滤掉已有歌词的专辑
    pending = []
    for album_id, artist, album, play_count in albums:
        safe_artist = artist.replace('/', '_').replace('\\', '_')
        safe_album = album.replace('/', '_').replace('\\', '_')
        album_dir = os.path.join(LYRICS_DIR, safe_artist, safe_album)
        
        if not os.path.exists(album_dir) or len([f for f in os.listdir(album_dir) if f.endswith('.lrc')]) < 3:
            pending.append((album_id, artist, album, play_count))
            if len(pending) >= limit:
                break
    
    return pending

def main():
    log('='*60)
    log('Cron任务：推进歌词计划')
    log('='*60)
    
    # 获取待处理专辑
    pending = get_pending_albums(limit=20)
    log(f'待处理专辑数: {len(pending)}')
    
    if not pending:
        log('没有待处理的中文专辑')
        return
    
    # 处理专辑
    conn = sqlite3.connect(DB)
    success_count = 0
    
    for album_id, artist, album, play_count in pending:
        try:
            result = process_album(album_id, conn)
            if result > 0:
                success_count += 1
            time.sleep(1)  # 避免请求过快
        except Exception as e:
            log(f'处理失败: {artist} - {album} - {e}')
    
    conn.close()
    
    log(f'本次处理完成: 成功={success_count}, 总数={len(pending)}')
    log('='*60)

if __name__ == '__main__':
    main()
