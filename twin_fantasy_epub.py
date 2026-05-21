#!/usr/bin/env python3
"""
Twin Fantasy 完整歌词电子书生成器
抓取所有歌词 → GLM翻译 → 生成EPUB → 发Kindle
"""
import asyncio, re, sys, os, json, urllib.request, urllib.parse, smtplib, hashlib, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from zipfile import ZipFile

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Twin Fantasy (Face to Face) 2018 完整曲目
TRACKLIST = [
    ("01", "My Boy (Twin Fantasy)", "myboytwinfantasy"),
    ("02", "Nervous Young Inhumans", "nervousyounginhumans"),
    ("03", "Bodys", "bodys"),
    ("04", "Cute Thing", "cutething"),
    ("05", "Stop Smoking (We Love You)", "stopsmoking"),
    ("06", "Sober To Death", "sobertodeath"),
    ("07", "Plane vs. Tank vs. Submarine", "GENIUS"),  # AZLyrics 没有，用 Genius
    ("08", "Beach Life-in-Death", "beachlifeindeath"),
    ("09", "Famous Prophets (Stars)", "famousprophetsstars"),
    ("10", "Twin Fantasy (Those Boys)", "twinfantasythoseboys"),
]

ZHIPU_API_KEY = "d30470492049453fbb58c8e713373d54.0VEj28B2KrfxC3Za"
SMTP_USER = "15206651142@163.com"
SMTP_PASS = "WWPkQKMPCMP4TPpx"
KINDLE_EMAIL = "JIMMYPAGELIMIT_ACFYFR@KINDLE.com"


# ============ 歌词获取 ============

def slugify(s):
    s = s.lower().strip()
    if s.startswith("the "):
        s = s[4:]
    return re.sub(r'[^a-z0-9]', '', s)

def fetch_lyrics_from_genius(artist, title):
    """从 Genius 抓取歌词（备用源）"""
    # Genius URL 格式: https://genius.com/Artist-title-lyrics
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
    slug = re.sub(r'\s+', '-', slug)
    url = f"https://genius.com/{artist.lower().replace(' ', '-')}-{slug}-lyrics"
    
    print(f"    尝试 Genius: {url}")
    
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html',
    })
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f"    Genius 请求失败: {e}")
        return None
    
    # Genius 歌词在 <div data-lyrics-container="true"> 里
    # 简单正则提取
    match = re.search(r'data-lyrics-container="true"[^>]*>(.*?)</div>', html, re.DOTALL)
    if not match:
        # 备用：找 lyrics 标记
        match = re.search(r'<div class="lyrics">(.*?)</div>', html, re.DOTALL)
    
    if match:
        raw = match.group(1)
        raw = re.sub(r'<[^>]+>', '', raw)  # 去标签
        raw = re.sub(r'\[.*?\]', '', raw)  # 去段落标记 [Verse], [Chorus] 等
        raw = raw.strip()
        return raw
    
    return None


def fetch_lyrics(title_slug):
    url = f"https://www.azlyrics.com/lyrics/carseatheadrest/{title_slug}.html"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html',
        'Accept-Language': 'en-US,en;q=0.9',
    })
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f"    请求失败: {e}")
        return None

    for marker in [
        "Usage of azlyrics.com content by any third-party",
        "Usage of azlyrics.com data by your application",
    ]:
        pos = html.find(marker)
        if pos != -1:
            break
    else:
        return None

    comment_end = html.find("-->", pos)
    if comment_end == -1:
        return None

    lyrics_start = comment_end + 3
    lyrics_end = html.find("</div>", lyrics_start)
    if lyrics_end == -1:
        return None

    raw = html[lyrics_start:lyrics_end]
    raw = re.sub(r'<br\s*/?>', '\n', raw, flags=re.IGNORECASE)
    raw = re.sub(r'<[^>]+>', '', raw)
    raw = re.sub(r'\r\n', '\n', raw)
    raw = re.sub(r'\n{3,}', '\n\n', raw)
    return raw.strip()


# ============ GLM 翻译 ============

def translate_glm(lyrics, song_title):
    paragraphs = [p.strip() for p in lyrics.split('\n\n') if p.strip()]
    
    prompt = f"""将以下歌曲《{song_title}》的英文歌词翻译成中文。

要求：
- 意译为主，保留诗意和情感
- 每段之间用 [SEP] 分隔（与原文段落一一对应）
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
        headers={
            "Authorization": f"Bearer {ZHIPU_API_KEY}",
            "Content-Type": "application/json"
        }
    )

    try:
        resp = urllib.request.urlopen(req, timeout=60)
        result = json.loads(resp.read())
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"    翻译失败: {e}")
        return None


def build_bilingual_html(title, lyrics, translation):
    """生成逐段中英对照 HTML"""
    en_paras = [p.strip() for p in lyrics.split('\n\n') if p.strip()]
    zh_paras = [p.strip() for p in translation.split('[SEP]') if p.strip()]

    html = f'<h2 class="song-title">{title}</h2>\n'
    
    for i in range(max(len(en_paras), len(zh_paras))):
        en = en_paras[i] if i < len(en_paras) else ""
        zh = zh_paras[i] if i < len(zh_paras) else ""
        
        en_lines = en.replace('\n', '<br/>')
        zh_lines = zh.replace('\n', '<br/>')
        
        html += f'''<div class="stanza">
  <p class="en">{en_lines}</p>
  <p class="zh">{zh_lines}</p>
</div>
'''
    
    html += '<hr class="song-divider"/>\n'
    return html


# ============ 生成 EPUB ============

def make_epub(songs_html, cover_path=None):
    epub_path = "C:/Users/15206/.qclaw/workspace/twin_fantasy_lyrics.epub"
    
    # 完整 HTML
    full_html = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
<meta charset="utf-8"/>
<title>Twin Fantasy - Car Seat Headrest (歌词中英对照)</title>
<style>
body {{
  font-family: "Georgia", serif;
  padding: 20px;
  line-height: 1.8;
  font-size: 1em;
  max-width: 800px;
  margin: 0 auto;
}}
h1 {{
  font-size: 1.8em;
  text-align: center;
  margin-bottom: 0.3em;
}}
.subtitle {{
  text-align: center;
  color: #666;
  margin-bottom: 2em;
  font-style: italic;
}}
h2.song-title {{
  font-size: 1.3em;
  margin-top: 2em;
  margin-bottom: 1em;
  border-bottom: 1px solid #ccc;
  padding-bottom: 0.3em;
}}
.stanza {{
  margin: 1em 0;
  padding: 0.8em;
  background: #f9f9f9;
  border-left: 3px solid #ddd;
}}
.en {{
  margin: 0 0 0.5em 0;
  color: #333;
  font-style: italic;
}}
.zh {{
  margin: 0;
  color: #555;
}}
hr.song-divider {{
  border: none;
  border-top: 2px solid #eee;
  margin: 2em 0;
}}
</style>
</head>
<body>
<h1>Twin Fantasy</h1>
<p class="subtitle">Car Seat Headrest (Face to Face, 2018)<br/>歌词中英对照</p>
{songs_html}
</body>
</html>"""

    container_xml = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
<rootfiles>
<rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
</rootfiles>
</container>"""

    content_opf = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:title>Twin Fantasy - Car Seat Headrest 歌词中英对照</dc:title>
<dc:creator>Car Seat Headrest</dc:creator>
<dc:language>zh</dc:language>
<dc:identifier id="uid">csh-twin-fantasy-lyrics</dc:identifier>
</metadata>
<manifest>
<item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
</manifest>
<spine>
<itemref idref="chapter1"/>
</spine>
</package>"""

    with ZipFile(epub_path, 'w') as zf:
        zf.writestr("mimetype", "application/epub+zip", compress_type=0)
        zf.writestr("META-INF/container.xml", container_xml)
        zf.writestr("OEBPS/content.opf", content_opf)
        zf.writestr("OEBPS/chapter1.xhtml", full_html)

    size = os.path.getsize(epub_path)
    print(f"\n✅ EPUB 生成: {epub_path} ({size//1024}KB)")
    return epub_path


# ============ 发送 Kindle ============

def send_kindle(epub_path):
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = KINDLE_EMAIL
    msg['Subject'] = "Convert"
    msg.attach(MIMEText("Twin Fantasy 歌词中英对照", 'plain', 'utf-8'))

    with open(epub_path, 'rb') as f:
        part = MIMEBase('application', 'epub+zip')
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="twin_fantasy_lyrics.epub"')
    msg.attach(part)

    print("发送到 Kindle...")
    with smtplib.SMTP_SSL("smtp.163.com", 465) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, KINDLE_EMAIL, msg.as_string())
    print("✅ 发送成功！")


# ============ 主流程 ============

def main():
    print("🎵 Twin Fantasy - Car Seat Headrest 歌词电子书生成器")
    print("=" * 55)
    
    all_songs_html = ""
    
    for num, title, slug in TRACKLIST:
        print(f"\n[{num}] {title}")
        
        # 1. 获取歌词
        print(f"  抓取歌词...")
        
        if slug == "GENIUS":
            # 用 Genius 作为备用源
            lyrics = fetch_lyrics_from_genius("Car Seat Headrest", title)
        else:
            lyrics = fetch_lyrics(slug)
        
        if not lyrics:
            print(f"  ⚠️  未找到歌词，跳过")
            all_songs_html += f'<h2 class="song-title">{num}. {title}</h2>\n<p><em>（歌词未找到）</em></p>\n<hr class="song-divider"/>\n'
            continue
        
        print(f"  ✅ 获取成功 ({len(lyrics)} 字符)")
        
        # 2. 翻译
        print(f"  翻译中...")
        translation = translate_glm(lyrics, title)
        
        if not translation:
            print(f"  ⚠️  翻译失败，只保留原文")
            translation = ""
        else:
            print(f"  ✅ 翻译完成")
        
        # 3. 生成 HTML
        song_html = build_bilingual_html(f"{num}. {title}", lyrics, translation)
        all_songs_html += song_html
        
        # 避免 API 限速
        time.sleep(2)
    
    # 4. 生成 EPUB
    epub_path = make_epub(all_songs_html)
    
    # 5. 发送 Kindle
    send_kindle(epub_path)
    
    print("\n🎉 完成！")

if __name__ == "__main__":
    main()
