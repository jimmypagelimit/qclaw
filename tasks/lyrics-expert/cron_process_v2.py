"""
Cron任务：推进歌词计划 v2
从tracks表获取待处理曲目，使用网易云API获取歌词
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
    """写入日志文件"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{timestamp}] {msg}'
    # 不再print到控制台，避免GBK编码错误
    # print(line)
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
        tlyric = data.get('tlyric', {}).get('lyric', '')
        return lrc or '', tlyric or ''
    except Exception as e:
        pass
    return '', ''

def save_lyrics(artist, album, track_name, track_num, lrc_text, trans_text=''):
    """保存歌词到文件，返回文件路径"""
    safe_artist = artist.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
    safe_album = album.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
    safe_track = track_name.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
    
    album_dir = os.path.join(LYRICS_DIR, safe_artist, safe_album)
    os.makedirs(album_dir, exist_ok=True)
    
    # 保存LRC
    lrc_path = None
    if lrc_text:
        lrc_path = os.path.join(album_dir, f'{track_num:02d}. {safe_track}.lrc')
        with open(lrc_path, 'w', encoding='utf-8') as f:
            f.write(lrc_text)
        
        # 保存纯文本（去除LRC时间戳）
        lines = []
        for line in lrc_text.split('\n'):
            if ']' in line:
                lines.append(line.split(']')[-1])
            else:
                lines.append(line)
        plain_text = '\n'.join(lines)
        txt_path = os.path.join(album_dir, f'{track_num:02d}. {safe_track}.txt')
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(plain_text)
    
    # 保存翻译
    if trans_text:
        trans_path = os.path.join(album_dir, f'{track_num:02d}. {safe_track}_trans.txt')
        with open(trans_path, 'w', encoding='utf-8') as f:
            f.write(trans_text)
    
    return lrc_path

def get_pending_tracks(limit=50):
    """获取待处理的中文库目"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    
    # 获取还没有歌词的中文曲目
    cur.execute("""
        SELECT t.id, t.album_id, t.track_number, t.track_name, 
               a.artist, a.album_name
        FROM tracks t
        JOIN albums a ON t.album_id = a.album_id
        WHERE (t.lyrics_text_path IS NULL OR t.lyrics_text_path = '')
          AND (a.album_name GLOB '*[一-龥]*' OR a.artist GLOB '*[一-龥]*')
        LIMIT ?
    """, (limit,))
    
    tracks = cur.fetchall()
    conn.close()
    
    return tracks

def process_track(track_id, album_id, track_num, track_name, artist, album):
    """处理单首曲目，获取歌词"""
    log(f'处理曲目: {artist} - {album} - {track_name}')
    
    # 搜索网易云
    song_id, found_name = wangyiyun_search(track_name, artist)
    if not song_id:
        log(f'  未找到歌曲: {track_name}')
        return False
    
    log(f'  找到歌曲: {found_name} (ID={song_id})')
    
    # 获取歌词
    lrc_text, trans_text = wangyiyun_lyric(song_id)
    if not lrc_text:
        log(f'  无歌词: {track_name}')
        return False
    
    # 保存歌词
    lrc_path = save_lyrics(artist, album, track_name, track_num, lrc_text, trans_text)
    
    # 更新数据库
    if lrc_path:
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute("""
            UPDATE tracks 
            SET lyrics_lrc_path = ?, lyrics_text_path = ?
            WHERE id = ?
        """, (lrc_path, lrc_path.replace('.lrc', '.txt'), track_id))
        conn.commit()
        conn.close()
        
        log(f'  已保存: {lrc_path}')
        return True
    
    return False

def main():
    log('='*60)
    log('Cron任务：推进歌词计划')
    log('='*60)
    
    # 获取待处理曲目
    tracks = get_pending_tracks(limit=30)
    log(f'待处理曲目数: {len(tracks)}')
    
    if not tracks:
        log('没有待处理的中文曲目')
        return
    
    # 处理曲目
    success = 0
    for track_id, album_id, track_num, track_name, artist, album in tracks:
        try:
            result = process_track(track_id, album_id, track_num, track_name, artist, album)
            if result:
                success += 1
            time.sleep(0.5)  # 避免请求过快
        except Exception as e:
            log(f'处理失败: {artist} - {track_name} - {e}')
    
    log(f'本次处理完成: 成功={success}, 总数={len(tracks)}')
    log('='*60)

if __name__ == '__main__':
    main()
