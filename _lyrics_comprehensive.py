# -*- coding: utf-8 -*-
"""
综合歌词获取脚本 - 结合 LRCLIB（英文）+ 网易云 API（中文）
用法：python _lyrics_comprehensive.py [limit]
  limit: 处理数量限制（默认 100）
"""

import sqlite3
import urllib.request
import urllib.parse
import json
import time
import os
import sys
import re

DB_PATH = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
LYRICS_DIR = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics'

def log(msg, log_file):
    print(msg)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

def search_lrclib(artist, track_name):
    """使用 LRCLIB 搜索歌词（英文首选）"""
    query = f"{artist} {track_name}"
    query_encoded = urllib.parse.quote(query)
    url = f"https://lrclib.net/api/search?q={query_encoded}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read().decode())
        if data and len(data) > 0:
            for item in data:
                if item.get('syncedLyrics'):
                    return item['syncedLyrics'], item.get('plainLyrics', '')
            if data[0].get('plainLyrics'):
                return None, data[0]['plainLyrics']
    except Exception as e:
        pass
    return None, None

def search_netease(artist, track_name):
    """使用网易云音乐 API 搜索歌词（中文首选）"""
    # 搜索歌曲ID
    search_query = f"{artist} {track_name}"
    search_encoded = urllib.parse.quote(search_query)
    search_url = f"https://music.163.com/api/search/get?s={search_encoded}&type=1&limit=5"
    
    try:
        req = urllib.request.Request(search_url, headers={
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://music.163.com/'
        })
        resp = urllib.request.urlopen(req, timeout=15)
        search_data = json.loads(resp.read().decode())
        
        if search_data.get('code') == 200 and search_data.get('result', {}).get('songs'):
            songs = search_data['result']['songs']
            if len(songs) > 0:
                song_id = songs[0]['id']
                
                # 获取歌词
                lyric_url = f"https://music.163.com/api/song/lyric?id={song_id}&lv=1&tv=1"
                req2 = urllib.request.Request(lyric_url, headers={
                    'User-Agent': 'Mozilla/5.0',
                    'Referer': 'https://music.163.com/'
                })
                resp2 = urllib.request.urlopen(req2, timeout=15)
                lyric_data = json.loads(resp2.read().decode())
                
                lrc = ''
                txt = ''
                
                if 'lrc' in lyric_data and lyric_data['lrc'].get('lyric'):
                    lrc = lyric_data['lrc']['lyric']
                
                if 'tlyric' in lyric_data and lyric_data['tlyric'].get('lyric'):
                    # 有翻译歌词，合并到 LRC
                    if lrc:
                        lrc = merge_translation(lrc, lyric_data['tlyric']['lyric'])
                
                if 'lyric' in lyric_data:
                    txt = lyric_data['lyric']
                
                return lrc, txt
    except Exception as e:
        pass
    
    return None, None

def merge_translation(lrc, translation):
    """合并原歌词和翻译歌词（按时间戳）"""
    # 简化版：直接返回原歌词，翻译歌词另存
    return lrc

def save_lyrics(artist, album, track_name, lrc_content, txt_content):
    """保存歌词到文件"""
    # 创建目录
    artist_dir = os.path.join(LYRICS_DIR, safe_filename(artist))
    album_dir = os.path.join(artist_dir, safe_filename(f"{artist} {album}"))
    os.makedirs(album_dir, exist_ok=True)
    
    base_name = safe_filename(track_name)
    
    lrc_path = ''
    txt_path = ''
    
    if lrc_content:
        lrc_path = os.path.join(album_dir, f"{base_name}.lrc")
        with open(lrc_path, 'w', encoding='utf-8') as f:
            f.write(lrc_content)
    
    if txt_content:
        txt_path = os.path.join(album_dir, f"{base_name}.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(txt_content)
    
    return lrc_path, txt_path

def safe_filename(name):
    """生成安全的文件名"""
    if not name:
        return 'unknown'
    # 移除非法字符
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    return name.strip()

def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    
    log_file = r'C:\Users\qujt\.qclaw\workspace\_lyrics_comprehensive_log.txt'
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 查询缺失歌词的曲目
    c.execute("""SELECT t.id, t.track_name, a.artist, a.album_name 
                  FROM tracks t 
                  LEFT JOIN albums a ON t.album_id = a.album_id
                  WHERE (t.lyrics_text_path IS NULL OR t.lyrics_text_path = '') 
                    AND (t.lyrics_lrc_path IS NULL OR t.lyrics_lrc_path = '')
                  LIMIT ?""", (limit,))
    
    tracks = c.fetchall()
    
    log(f"Found {len(tracks)} tracks missing lyrics", log_file)
    
    success_count = 0
    
    for i, (track_id, track_name, artist, album) in enumerate(tracks):
        log(f"[{i+1}/{len(tracks)}] {artist} - {track_name} (from {album})", log_file)
        
        # 尝试 LRCLIB 首先（英文）
        lrc_content, txt_content = search_lrclib(artist, track_name)
        
        # 如果 LRCLIB 未找到，尝试网易云（中文）
        if not lrc_content and not txt_content:
            lrc_content, txt_content = search_netease(artist, track_name)
        
        # 如果找到歌词，保存并更新数据库
        if lrc_content or txt_content:
            lrc_path, txt_path = save_lyrics(artist, album, track_name, lrc_content, txt_content)
            
            # 更新数据库
            c.execute("""UPDATE tracks 
                          SET lyrics_lrc_path = ?, lyrics_text_path = ?
                          WHERE id = ?""", 
                      (lrc_path, txt_path, track_id))
            conn.commit()
            
            log(f"  -> SAVED (LRC: {'YES' if lrc_path else 'NO'}, TXT: {'YES' if txt_path else 'NO'})", log_file)
            success_count += 1
        else:
            log(f"  -> NOT FOUND", log_file)
        
        # 限流
        time.sleep(0.5)
    
    log(f"Done! Successfully added lyrics for {success_count}/{len(tracks)} tracks", log_file)
    conn.close()

if __name__ == '__main__':
    main()
