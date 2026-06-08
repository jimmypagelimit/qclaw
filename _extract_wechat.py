import re

with open('C:/Users/qujt/.qclaw/workspace/_temp_wechat.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 提取文章正文
match = re.search(r'<div class="rich_media_content[^"]*" id="js_content"[^>]*>(.*?)</div>\s*<div', html, re.DOTALL)
if match:
    content = match.group(1)
    # 移除HTML标签
    text = re.sub(r'<[^>]+>', ' ', content)
    text = re.sub(r'&[a-z]+;', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    print(text[:4000])
else:
    # 尝试另一种方式
    idx = html.find('CloakBrowser')
    if idx > 0:
        text = re.sub(r'<[^>]+>', ' ', html[idx-500:idx+3000])
        text = re.sub(r'\s+', ' ', text)
        print(text)
