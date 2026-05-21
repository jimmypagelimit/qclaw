#!/usr/bin/env python3
"""生成 Twin Fantasy 歌词 EPUB（已完成的 8 首 + 手动补 2 首）"""
import os, sys, smtplib, re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from zipfile import ZipFile

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# 已完成的歌词文件
lyrics_dir = "C:/Users/15206/.qclaw/workspace/lyrics/"
completed_songs = [
    ("01", "My Boy (Twin Fantasy)", "My Boy.txt"),
    ("02", "Nervous Young Inhumans", "Nervous Young Inhumans.txt"),
    ("03", "Bodys", "Bodys.txt"),
    ("04", "Cute Thing", "Cute Thing.txt"),
    ("05", "Stop Smoking (We Love You)", "Stop Smoking.txt"),
    ("06", "Sober To Death", "Sober To Death.txt"),
    ("08", "Beach Life-in-Death", "Beach Life-in-Death.txt"),
    ("09", "Famous Prophets (Stars)", "Famous Prophets.txt"),
    ("10", "Twin Fantasy (Those Boys)", "Twin Fantasy.txt"),
]

def read_lyrics(filename):
    path = os.path.join(lyrics_dir, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def make_epub():
    all_html = ""
    
    for num, title, filename in completed_songs:
        content = read_lyrics(filename)
        if not content:
            print(f"⚠️ {title} - 文件不存在")
            continue
        
        # 解析中英对照
        parts = content.split("--- 翻译 ---")
        lyrics = parts[0].replace(title, "").strip() if parts else content
        translation = parts[1].strip() if len(parts) > 1 else ""
        
        # 分段
        en_paras = [p.strip() for p in lyrics.split('\n\n') if p.strip()]
        zh_paras = [p.strip() for p in translation.split('[SEP]') if p.strip()]
        
        song_html = f'<h2 class="song-title">{num}. {title}</h2>\n'
        
        for i in range(max(len(en_paras), len(zh_paras))):
            en = en_paras[i].replace('\n', '<br/>') if i < len(en_paras) else ""
            zh = zh_paras[i].replace('\n', '<br/>') if i < len(zh_paras) else ""
            
            if en or zh:
                song_html += f'''<div class="stanza">
  <p class="en">{en}</p>
  <p class="zh">{zh}</p>
</div>
'''
        
        song_html += '<hr class="song-divider"/>\n'
        all_html += song_html
        print(f"✅ {title}")
    
    # Plane vs. Tank 手动提示
    all_html += '''<h2 class="song-title">07. Plane vs. Tank vs. Submarine</h2>
<div class="stanza">
<p class="en"><em>歌词来源暂不可用</em></p>
<p class="zh">Genius/Musixmatch 均被 Cloudflare 拦截，需手动补充</p>
</div>
<hr class="song-divider"/>
'''
    
    # 完整 HTML
    full_html = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
<meta charset="utf-8"/>
<title>Twin Fantasy - Car Seat Headrest</title>
<style>
body {{
  font-family: "Georgia", serif;
  padding: 20px;
  line-height: 1.8;
  font-size: 1em;
  max-width: 800px;
  margin: 0 auto;
}}
h1 {{ font-size: 1.8em; text-align: center; margin-bottom: 0.3em; }}
.subtitle {{ text-align: center; color: #666; margin-bottom: 2em; font-style: italic; }}
h2.song-title {{ font-size: 1.3em; margin-top: 2em; margin-bottom: 1em; border-bottom: 1px solid #ccc; padding-bottom: 0.3em; }}
.stanza {{ margin: 1em 0; padding: 0.8em; background: #f9f9f9; border-left: 3px solid #ddd; }}
.en {{ margin: 0 0 0.5em 0; color: #333; font-style: italic; }}
.zh {{ margin: 0; color: #555; }}
hr.song-divider {{ border: none; border-top: 2px solid #eee; margin: 2em 0; }}
</style>
</head>
<body>
<h1>Twin Fantasy</h1>
<p class="subtitle">Car Seat Headrest (Face to Face, 2018)<br/>歌词中英对照 · 9/10 首完成</p>
{all_html}
</body>
</html>"""

    # EPUB
    epub_path = "C:/Users/15206/.qclaw/workspace/twin_fantasy_lyrics_v2.epub"
    
    container_xml = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
<rootfiles>
<rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
</rootfiles>
</container>"""

    content_opf = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:title>Twin Fantasy 歌词中英对照</dc:title>
<dc:creator>Car Seat Headrest</dc:creator>
<dc:language>zh</dc:language>
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

    print(f"\n✅ EPUB: {epub_path} ({os.path.getsize(epub_path)//1024}KB)")
    return epub_path

def send_kindle(epub_path):
    msg = MIMEMultipart()
    msg['From'] = "15206651142@163.com"
    msg['To'] = "JIMMYPAGELIMIT_ACFYFR@KINDLE.com"
    msg['Subject'] = "Convert"
    msg.attach(MIMEText("Twin Fantasy 歌词 (9/10)", 'plain', 'utf-8'))

    with open(epub_path, 'rb') as f:
        part = MIMEBase('application', 'epub+zip')
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="twin_fantasy.epub"')
    msg.attach(part)

    print("发送到 Kindle...")
    with smtplib.SMTP_SSL("smtp.163.com", 465) as server:
        server.login("15206651142@163.com", "WWPkQKMPCMP4TPpx")
        server.sendmail("15206651142@163.com", "JIMMYPAGELIMIT_ACFYFR@KINDLE.com", msg.as_string())
    print("✅ 发送成功！")

epub_path = make_epub()
send_kindle(epub_path)
