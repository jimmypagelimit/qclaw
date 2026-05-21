#!/usr/bin/env python3
"""补全 Twin Fantasy 缺失的 2 首歌词"""
import urllib.request, json, re, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

ZHIPU_API_KEY = "d30470492049453fbb58c8e713373d54.0VEj28B2KrfxC3Za"

def fetch_azlyrics(slug):
    url = f"https://www.azlyrics.com/lyrics/carseatheadrest/{slug}.html"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        return None, str(e)
    
    for marker in ["Usage of azlyrics.com content by any third-party", "Usage of azlyrics.com data by your application"]:
        pos = html.find(marker)
        if pos != -1:
            break
    else:
        return None, "No lyrics marker"
    
    comment_end = html.find("-->", pos)
    if comment_end == -1:
        return None, "No comment end"
    
    lyrics_start = comment_end + 3
    lyrics_end = html.find("</div>", lyrics_start)
    if lyrics_end == -1:
        return None, "No </div>"
    
    raw = html[lyrics_start:lyrics_end]
    raw = re.sub(r'<br\s*/?>', '\n', raw, flags=re.IGNORECASE)
    raw = re.sub(r'<[^>]+>', '', raw)
    raw = re.sub(r'\r\n', '\n', raw)
    raw = re.sub(r'\n{3,}', '\n\n', raw)
    return raw.strip(), None

def translate_glm(lyrics, title):
    paragraphs = [p.strip() for p in lyrics.split('\n\n') if p.strip()]
    prompt = f"""将以下歌曲《{title}》的英文歌词翻译成中文。

要求：
- 意译为主，保留诗意和情感
- 每段之间用 [SEP] 分隔
- 不要加任何解释，只输出翻译

歌词：
{('[SEP]' + chr(10)).join(paragraphs)}

翻译："""

    data = json.dumps({
        "model": "glm-4-flash",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }).encode()

    req = urllib.request.Request(
        "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        data=data,
        headers={"Authorization": f"Bearer {ZHIPU_API_KEY}", "Content-Type": "application/json"}
    )
    try:
        resp = urllib.request.urlopen(req, timeout=60)
        result = json.loads(resp.read())
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return None

# 1. Stop Smoking - AZLyrics
print("[05] Stop Smoking (We Love You)")
lyrics, err = fetch_azlyrics("stopsmoking")
if lyrics:
    print(f"  ✅ 歌词获取成功 ({len(lyrics)} 字符)")
    translation = translate_glm(lyrics, "Stop Smoking (We Love You)")
    if translation:
        print(f"  ✅ 翻译完成")
        # 保存
        with open("C:/Users/15206/.qclaw/workspace/lyrics/Stop Smoking.txt", "w", encoding="utf-8") as f:
            f.write(f"Stop Smoking (We Love You)\n\n{lyrics}\n\n--- 翻译 ---\n\n{translation}")
        print(f"  ✅ 已保存")
else:
    print(f"  ❌ 获取失败: {err}")

time.sleep(1)

# 2. Plane vs. Tank vs. Submarine - 用已有的翻译接口，先查是否有其他来源
print("\n[07] Plane vs. Tank vs. Submarine")
print("  AZLyrics 无此歌曲，尝试其他来源...")

# 直接从 genius.com 的公开 API 搜索（不需要 token）
try:
    search_url = "https://genius.com/api/search?q=Car%20Seat%20Headrest%20Plane%20vs%20Tank%20vs%20Submarine"
    req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read())
    
    hits = data.get("response", {}).get("hits", [])
    if hits:
        song_url = hits[0]["result"]["url"]
        print(f"  找到 Genius: {song_url}")
        
        # 抓取页面
        page_req = urllib.request.Request(song_url, headers={'User-Agent': 'Mozilla/5.0'})
        page_resp = urllib.request.urlopen(page_req, timeout=15)
        page_html = page_resp.read().decode('utf-8', errors='replace')
        
        # Genius 的歌词在 JSON-LD 里
        import re
        lyric_match = re.search(r'"lyrics"\s*:\s*"([^"]*(?:\\.[^"]*)*)"', page_html)
        if lyric_match:
            import codecs
            lyrics = codecs.decode(lyric_match.group(1), 'unicode_escape')
            lyrics = re.sub(r'<[^>]+>', '', lyrics)  # 去掉 HTML 标签
            lyrics = re.sub(r'\[.*?\]', '', lyrics)  # 去掉 [Verse], [Chorus] 等
            lyrics = re.sub(r'\n{3,}', '\n\n', lyrics.strip())
            print(f"  ✅ 歌词获取成功 ({len(lyrics)} 字符)")
            
            translation = translate_glm(lyrics, "Plane vs. Tank vs. Submarine")
            if translation:
                print(f"  ✅ 翻译完成")
                with open("C:/Users/15206/.qclaw/workspace/lyrics/Plane vs Tank vs Submarine.txt", "w", encoding="utf-8") as f:
                    f.write(f"Plane vs. Tank vs. Submarine\n\n{lyrics}\n\n--- 翻译 ---\n\n{translation}")
                print(f"  ✅ 已保存")
        else:
            print(f"  ❌ 未找到歌词内容")
    else:
        print(f"  ❌ Genius 也找不到")
except Exception as e:
    print(f"  ❌ Genius 搜索失败: {e}")
