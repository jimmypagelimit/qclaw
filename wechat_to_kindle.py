#!/usr/bin/env python3
"""微信公众号文章 → MOBI"""
import asyncio, re, sys, os, subprocess, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def fetch_wechat():
    from playwright.async_api import async_playwright
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        url = "https://mp.weixin.qq.com/s/olYbVOqTIvfoJ6DAhwVNdQ"
        print(f"打开: {url}")
        await page.goto(url, timeout=60000, wait_until="domcontentloaded")
        await asyncio.sleep(5)  # 等待 JS 渲染
        
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
        print(f"作者: {author}")
        
        # 提取正文
        content_elem = await page.query_selector("#js_content")
        if content_elem:
            text = await content_elem.inner_text()
            html = await content_elem.inner_html()
        else:
            text = "未找到正文"
            html = ""
        
        print(f"正文长度: {len(text)} 字符")
        
        await browser.close()
        return title, author, text, html

def make_mobi(title, author, text):
    """生成简易 HTML 用于转 MOBI"""
    paragraphs = "\n".join(f"<p>{p.strip()}</p>" for p in text.split('\n') if p.strip())
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
body {{ font-family: serif; padding: 20px; line-height: 1.8; }}
h1 {{ font-size: 1.5em; }}
.author {{ color: #666; margin-bottom: 20px; }}
.content {{ text-align: justify; }}
</style>
</head>
<body>
<h1>{title}</h1>
<p class="author">来源: {author}</p>
<div class="content">
{paragraphs}
</div>
</body>
</html>"""
    
    md_path = "C:/Users/15206/.qclaw/workspace/wechat_article.md"
    html_path = "C:/Users/15206/.qclaw/workspace/wechat_article.html"
    mobi_path = "C:/Users/15206/.qclaw/workspace/wechat_article.mobi"
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(text)
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    # 转 MOBI
    cmd = [
        "C:/Program Files/Calibre2/ebook-convert.exe",
        html_path, mobi_path,
        "--title", title,
        "--authors", author,
        "--language", "zh"
    ]
    print("转换 MOBI...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ MOBI 生成成功")
        return mobi_path
    else:
        print(f"❌ 转换失败: {result.stderr}")
        return None

def send_kindle(mobi_path):
    SMTP_HOST = "smtp.163.com"
    SMTP_PORT = 465
    SMTP_USER = "15206651142@163.com"
    SMTP_PASS = "WWPkQKMPCMP4TPpx"
    
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = "JIMMYPAGELIMIT_ACFYFR@KINDLE.com"
    msg['Subject'] = "Convert"
    msg.attach(MIMEText("微信文章", 'plain', 'utf-8'))
    
    with open(mobi_path, 'rb') as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="wechat_article.mobi"')
    msg.attach(part)
    
    print("发送到 Kindle...")
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, "JIMMYPAGELIMIT_ACFYFR@KINDLE.com", msg.as_string())
    print("✅ 发送成功！")

async def main():
    title, author, text, html = await fetch_wechat()
    
    # 保存正文
    with open("C:/Users/15206/.qclaw/workspace/wechat_text.txt", 'w', encoding='utf-8') as f:
        f.write(f"{title}\n\n作者: {author}\n\n{text}")
    print(f"\n正文已保存到: wechat_text.txt")
    print(f"预览（前500字）:\n{text[:500]}")
    
    # 发截图看效果
    print("\n截图已保存: wechat_article.png")
    
    # 转 MOBI
    mobi_path = make_mobi(title, author, text)
    if mobi_path:
        send_kindle(mobi_path)

asyncio.run(main())
