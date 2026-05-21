#!/usr/bin/env python3
"""Genius 歌词抓取 - 完整版"""
import os
import re
import subprocess
import sys
import time

SONG_URLS = [
    "https://genius.com/Wait-what-did-you-say-the-city-lyrics",
    "https://genius.com/Wait-what-did-you-say-would-it-kill-you-to-just-be-a-little-less-loud-lyrics",
    "https://genius.com/Wait-what-did-you-say-illiterate-lol-do-you-get-it-lyrics",
    "https://genius.com/Wait-what-did-you-say-whats-a-song-about-lyrics",
    "https://genius.com/Wait-what-did-you-say-you-shouldnt-listen-to-me-lyrics",
    "https://genius.com/Wait-what-did-you-say-everythings-worthless-everythings-worth-it-lyrics",
    "https://genius.com/Wait-what-did-you-say-coward-lyrics",
    "https://genius.com/Wait-what-did-you-say-buddy-lyrics",
    "https://genius.com/Wait-what-did-you-say-721-lyrics",
    "https://genius.com/Wait-what-did-you-say-i-slept-for-twenty-four-hours-lyrics",
]


def fetch_page(url: str) -> str:
    cmd = ["curl", "-s", "-L", "-H", "User-Agent: Mozilla/5.0", url]
    result = subprocess.run(cmd, capture_output=True)
    return result.stdout.decode("utf-8", errors="replace")


def extract_lyrics(html: str) -> str:
    """提取歌词 - 从 JSON 数据中提取"""
    # 方法1: 从 window.__PRELOADED_STATE__ 中提取
    match = re.search(r'"lyrics"\s*:\s*\{[^}]*"body"\s*:\s*\{[^}]*"html"\s*:\s*"([^"]+)"', html)
    if match:
        lyrics = match.group(1)
        # 解码 JSON 字符串
        lyrics = lyrics.replace("\\n", "\n").replace("\\/", "/").replace('\\"', '"')
        lyrics = re.sub(r'<[^>]+>', '', lyrics)  # 移除 HTML 标签
        return lyrics.strip()
    
    # 方法2: 从 data-lyrics-container 提取
    matches = re.findall(r'data-lyrics-container="true"[^>]*>([^<]+)', html)
    if matches:
        return "\n".join(matches).strip()
    
    return ""


def extract_song_name(url: str) -> str:
    match = re.search(r"Wait-what-did-you-say-(.+)-lyrics", url)
    if match:
        return match.group(1).replace("-", " ").title()
    return "Unknown"


def main():
    output_dir = "lyrics/Wait-What-Did-You-Say"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"抓取 Wait, What Did You Say? 歌词...")
    print(f"共 {len(SONG_URLS)} 首\n")
    
    success = 0
    for i, url in enumerate(SONG_URLS, 1):
        song_name = extract_song_name(url)
        print(f"[{i}/{len(SONG_URLS)}] {song_name}")
        
        html = fetch_page(url)
        lyrics = extract_lyrics(html)
        
        if lyrics and len(lyrics) > 20:
            output_file = os.path.join(output_dir, f"{song_name.replace(' ', '-')}.txt")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"{song_name}\n{'=' * len(song_name)}\n\n{lyrics}")
            print(f"  ✓ 已保存")
            success += 1
        else:
            # 保存 HTML 用于调试
            debug_file = os.path.join(output_dir, f"debug_{song_name.replace(' ', '-')}.html")
            with open(debug_file, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"  ✗ 未找到歌词，已保存调试文件")
        
        time.sleep(0.3)
    
    print(f"\n完成! 成功抓取 {success}/{len(SONG_URLS)} 首")
    print(f"输出目录: {output_dir}")


if __name__ == "__main__":
    main()
