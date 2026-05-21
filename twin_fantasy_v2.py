#!/usr/bin/env python3
"""
Twin Fantasy 完整歌词电子书生成器 v2
- 抓取所有歌词 → GLM翻译 → 保存到 lyrics/ → 生成EPUB → 发Kindle
"""
import re, sys, os, json, urllib.request, time, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from zipfile import ZipFile

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Twin Fantasy (Face to Face) 2018 曲目 + 正确的 slug
TRACKLIST = [
    ("01", "My Boy (Twin Fantasy)", "myboytwinfantasy"),
    ("02", "Nervous Young Inhumans", "nervousyounginhumans"),
    ("03", "Bodys", "bodys"),
    ("04", "Cute Thing", "cutething"),
    ("05", "Stop Smoking (We Love You)", "stopsmoking"),
    ("06", "Sober To Death", "sobertodeath"),
    ("07", "Plane vs. Tank vs. Submarine", None),  # AZLyrics 没有
    ("08", "Beach Life-in-Death", "beachlifeindeath"),
    ("09", "Famous Prophets (Stars)", "famousprophetsstars"),
    ("10", "Twin Fantasy (Those Boys)", "twinfantasythoseboys"),
]

ZHIPU_API_KEY = "d30470492049453fbb58c8e713373d54.0VEj28B2KrfxC3Za"
LYRICS_DIR = "C:/Users/15206/.qclaw/workspace/lyrics_twin_fantasy/"
os.makedirs(LYRICS_DIR, exist_ok=True)

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
        return None, "No marker"
    
    comment_end = html.find("-->", pos)
    lyrics_start = comment_end + 3
    lyrics_end = html.find("</div>", lyrics_start)
    
    raw = html[lyrics_start:lyrics_end]
    raw = re.sub(r'<br\s*/?>', '\n', raw, flags=re.IGNORECASE)
    raw = re.sub(r'<[^>]+>', '', raw)
    raw = re.sub(r'\r\n', '\n', raw)
    raw = re.sub(r'\n{3,}', '\n\n', raw)
    return raw.strip(), None

def translate_glm(lyrics, title):
    paragraphs = [p.strip() for p in lyrics.split('\n\n') if p.strip()]
    if not paragraphs:
        return None
    
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
        print(f"    翻译失败: {e}")
        return None

def make_epub(songs_data):
    epub_path = "C:/Users/15206/.qclaw/workspace/twin_fantasy_complete.epub"
    
    all_html = ""
    for num, title, lyrics, translation in songs_data:
        if not lyrics:
            all_html += f'''<h2 class="song-title">{num}. {title}</h2>
<div class="stanza"><p class="en"><em>歌词暂不可用</em></p></div>
<hr class="song-divider"/>
'''
            continue
        
        en_paras = [p.strip() for p in lyrics.split('\n\n') if p.strip()]
        zh_paras = [p.strip() for p in (translation or "").split('[SEP]') if p.strip()]
        
        song_html = f'<h2 class="song-title">{num}. {title}</h2>\n'
        for i in range(max(len(en_paras), len(zh_paras))):
            en = en_paras[i].replace('\n', '<br/>') if i < len(en_paras) else ""
            zh = zh_paras[i].replace('\n', '<br/>') if i < len(zh_paras) else ""
            if en or zh:
                song_html += f'<div class="stanza"><p class="en">{en}</p><p class="zh">{zh}</p></div>\n'
        song_html += '<hr class="song-divider"/>\n'
        all_html += song_html
    
    full_html = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><meta charset="utf-8"/><title>Twin Fantasy</title>
<style>
body {{ font-family: Georgia, serif; padding: 20px; line-height: 1.8; max-width: 800px; margin: 0 auto; }}
h1 {{ font-size: 1.8em; text-align: center; }}
.subtitle {{ text-align: center; color: #666; margin-bottom: 2em; font-style: italic; }}
h2.song-title {{ font-size: 1.3em; margin-top: 2em; border-bottom: 1px solid #ccc; padding-bottom: 0.3em; }}
.stanza {{ margin: 1em 0; padding: 0.8em; background: #f9f9f9; border-left: 3px solid #ddd; }}
.en {{ margin: 0 0 0.5em 0; color: #333; font-style: italic; }}
.zh {{ margin: 0; color: #555; }}
hr.song-divider {{ border: none; border-top: 2px solid #eee; margin: 2em 0; }}
</style>
</head>
<body>
<h1>Twin Fantasy</h1>
<p class="subtitle">Car Seat Headrest (Face to Face, 2018)<br/>歌词中英对照</p>
{all_html}
</body>
</html>"""

    container_xml = """<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>"""

    content_opf = """<?xml version="1.0"?><package xmlns="http://www.idpf.org/2007/opf" version="3.0">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:title>Twin Fantasy 歌词中英对照</dc:title>
<dc:creator>Car Seat Headrest</dc:creator>
<dc:language>zh</dc:language>
</metadata>
<manifest><item id="c1" href="chapter1.xhtml" media-type="application/xhtml+xml"/></manifest>
<spine><itemref idref="c1"/></spine>
</package>"""

    with ZipFile(epub_path, 'w') as zf:
        zf.writestr("mimetype", "application/epub+zip", compress_type=0)
        zf.writestr("META-INF/container.xml", container_xml)
        zf.writestr("OEBPS/content.opf", content_opf)
        zf.writestr("OEBPS/chapter1.xhtml", full_html)

    return epub_path

def send_kindle(epub_path):
    msg = MIMEMultipart()
    msg['From'] = "15206651142@163.com"
    msg['To'] = "JIMMYPAGELIMIT_ACFYFR@KINDLE.com"
    msg['Subject'] = "Convert"
    msg.attach(MIMEText("Twin Fantasy 歌词中英对照", 'plain', 'utf-8'))

    with open(epub_path, 'rb') as f:
        part = MIMEBase('application', 'epub+zip')
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="twin_fantasy.epub"')
    msg.attach(part)

    with smtplib.SMTP_SSL("smtp.163.com", 465) as server:
        server.login("15206651142@163.com", "WWPkQKMPCMP4TPpx")
        server.sendmail("15206651142@163.com", "JIMMYPAGELIMIT_ACFYFR@KINDLE.com", msg.as_string())
    print("✅ 发送到 Kindle 成功！")

def main():
    print("🎵 Twin Fantasy 歌词电子书生成器 v2")
    print("=" * 50)
    
    songs_data = []
    
    for num, title, slug in TRACKLIST:
        print(f"\n[{num}] {title}")
        
        if slug is None:
            print(f"  ⚠️  无歌词来源")
            songs_data.append((num, title, None, None))
            continue
        
        # 抓取歌词
        lyrics, err = fetch_azlyrics(slug)
        if not lyrics:
            print(f"  ❌ 获取失败: {err}")
            songs_data.append((num, title, None, None))
            continue
        
        print(f"  ✅ 歌词 {len(lyrics)} 字符")
        
        # 翻译
        print(f"  翻译中...")
        translation = translate_glm(lyrics, title)
        if translation:
            print(f"  ✅ 翻译完成")
        else:
            translation = ""
        
        # 保存
        filepath = os.path.join(LYRICS_DIR, f"{num}. {title}.txt")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"{title}\n\n{lyrics}\n\n--- 翻译 ---\n\n{translation}")
        print(f"  ✅ 已保存")
        
        songs_data.append((num, title, lyrics, translation))
        time.sleep(2)  # 避免限速
    
    # 生成 EPUB
    print("\n生成 EPUB...")
    epub_path = make_epub(songs_data)
    size = os.path.getsize(epub_path) // 1024
    print(f"✅ {epub_path} ({size}KB)")
    
    # 发送
    send_kindle(epub_path)
    
    # 统计
    success = sum(1 for _, _, l, _ in songs_data if l)
    print(f"\n🎉 完成！成功 {success}/10 首")

if __name__ == "__main__":
    main()
