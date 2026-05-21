#!/usr/bin/env python3
"""微信公众号文章 → EPUB（保留图片和排版）"""
import asyncio, re, sys, os, subprocess, smtplib, hashlib
import urllib.request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from zipfile import ZipFile
from io import BytesIO

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def fetch_wechat():
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        url = "https://mp.weixin.qq.com/s/8KyXZdehNVK7vFPxgLXCCA"
        print(f"打开: {url}")
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        await asyncio.sleep(5)
        
        # 截图
        await page.screenshot(path="C:/Users/15206/.qclaw/workspace/wechat_article.png")
        print("截图已保存")
        
        # 提取标题
        title_elem = await page.query_selector("#activity-name")
        title = await title_elem.inner_text() if title_elem else "无标题"
        print(f"标题: {title}")
        
        # 提取作者
        author_elem = await page.query_selector("#js_name")
        author = await author_elem.inner_text() if author_elem else "未知作者"
        
        # 提取正文 HTML
        content_elem = await page.query_selector("#js_content")
        html_content = await content_elem.inner_html() if content_elem else ""
        
        await browser.close()
        return title, author, html_content

def download_images(html_content):
    """下载文章中的图片，返回替换后的HTML和本地路径列表"""
    img_dir = "C:/Users/15206/.qclaw/workspace/wechat_images"
    os.makedirs(img_dir, exist_ok=True)
    
    # 找到所有图片 URL
    img_urls = re.findall(r'(https?://mmbiz\.qpic\.cn/[^\s"\'<>]+)', html_content)
    print(f"找到 {len(img_urls)} 张图片")
    
    local_images = {}
    for i, url in enumerate(set(img_urls)):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0',
                'Referer': 'https://mp.weixin.qq.com/'
            })
            resp = urllib.request.urlopen(req, timeout=30)
            data = resp.read()
            
            # 根据URL生成文件名
            ext = re.search(r'\.(jpg|jpeg|png|gif|webp)', url, re.I)
            ext = ext.group(1) if ext else 'jpg'
            filename = f"img_{i}.{ext}"
            filepath = os.path.join(img_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(data)
            print(f"  下载: {filename} ({len(data)//1024}KB)")
            
            local_images[url] = f"images/{filename}"
        except Exception as e:
            print(f"  下载失败: {url[:50]}... - {e}")
    
    # 替换HTML中的图片URL为本地路径
    def replace_url(match):
        url = match.group(1)
        if url in local_images:
            return f'src="{local_images[url]}"'
        return match.group(0)
    
    html_content = re.sub(r'src=["\']([^"\']+)["\']', replace_url, html_content)
    return html_content, img_dir, local_images

def make_epub(title, author, html_content, img_dir, local_images):
    """生成 EPUB 文件"""
    epub_path = "C:/Users/15206/.qclaw/workspace/wechat_article_v2.epub"
    
    # 清理HTML，移除微信特定样式
    html_content = re.sub(r'style="[^"]*"', '', html_content)
    html_content = re.sub(r'<p[^>]*>\s*</p>', '', html_content)
    html_content = re.sub(r'<span[^>]*>(.*?)</span>', r'\1', html_content)
    html_content = re.sub(r'<section[^>]*>', '', html_content)
    html_content = re.sub(r'</section>', '', html_content)
    
    # 完整的XHTML
    xhtml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
<meta charset="utf-8"/>
<title>{title}</title>
<style>
body {{ font-family: "Georgia", serif; padding: 20px; line-height: 1.8; font-size: 1.1em; }}
h1 {{ font-size: 1.5em; line-height: 1.4; }}
.author {{ color: #666; margin-bottom: 20px; font-size: 0.9em; }}
p {{ margin: 0.8em 0; text-indent: 2em; }}
img {{ max-width: 100%; height: auto; margin: 1em 0; }}
</style>
</head>
<body>
<h1>{title}</h1>
<p class="author">来源: {author}</p>
<div class="content">
{html_content}
</div>
</body>
</html>"""
    
    # EPUB元数据
    container_xml = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
<rootfiles>
<rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
</rootfiles>
</container>"""
    
    content_opf = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:title>{title}</dc:title>
<dc:creator>{author}</dc:creator>
<dc:language>zh</dc:language>
<dc:identifier id="uid">wechat-{hashlib.md5(title.encode()).hexdigest()[:8]}</dc:identifier>
</metadata>
<manifest>
<item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>
"""
    
    # 添加图片到manifest
    for url, path in local_images.items():
        ext = os.path.splitext(path)[1][1:]
        mime = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png', 'gif': 'image/gif', 'webp': 'image/webp'}.get(ext, 'image/jpeg')
        item_id = path.replace('/', '_').replace('.', '_')
        content_opf += f'<item id="{item_id}" href="{path}" media-type="{mime}"/>\n'
    
    content_opf += """</manifest>
<spine>
<itemref idref="chapter1"/>
</spine>
</package>"""
    
    toc_xhtml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>{title}</title></head>
<body>
<nav epub:type="toc">
<h1>{title}</h1>
<ol>
<li><a href="chapter1.xhtml">{title}</a></li>
</ol>
</nav>
</body>
</html>"""
    
    # 创建 EPUB（ZIP格式）
    with ZipFile(epub_path, 'w') as zf:
        zf.writestr("mimetype", "application/epub+zip", compress_type=0)
        zf.writestr("META-INF/container.xml", container_xml)
        zf.writestr("OEBPS/content.opf", content_opf)
        zf.writestr("OEBPS/toc.xhtml", toc_xhtml)
        zf.writestr("OEBPS/chapter1.xhtml", xhtml)
        
        # 添加图片
        for url, path in local_images.items():
            full_path = os.path.join(img_dir, os.path.basename(path))
            if os.path.exists(full_path):
                zf.write(full_path, f"OEBPS/{path}")
    
    print(f"✅ EPUB 已生成: {epub_path}")
    return epub_path

def send_kindle(epub_path):
    SMTP_HOST = "smtp.163.com"
    SMTP_PORT = 465
    SMTP_USER = "15206651142@163.com"
    SMTP_PASS = "WWPkQKMPCMP4TPpx"
    
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = "JIMMYPAGELIMIT_ACFYFR@KINDLE.com"
    msg['Subject'] = "Convert"
    msg.attach(MIMEText("微信文章 EPUB", 'plain', 'utf-8'))
    
    with open(epub_path, 'rb') as f:
        part = MIMEBase('application', 'epub+zip')
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="wechat_article.epub"')
    msg.attach(part)
    
    print("发送到 Kindle...")
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, "JIMMYPAGELIMIT_ACFYFR@KINDLE.com", msg.as_string())
    print("✅ 发送成功！")

async def main():
    title, author, html_content = await fetch_wechat()
    
    # 下载图片并替换URL
    html_content, img_dir, local_images = download_images(html_content)
    
    # 生成 EPUB
    epub_path = make_epub(title, author, html_content, img_dir, local_images)
    
    # 发送到 Kindle
    send_kindle(epub_path)

asyncio.run(main())
