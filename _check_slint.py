import re
with open(r'C:\Users\qujt\.qclaw\workspace\_slint_ok.html', encoding='utf-8') as f:
    html = f.read()
print('大小:', len(html))
m = re.search(r'<title>(.*?)</title>', html)
if m: print('Title:', m.group(1))
entries = re.findall(r'class="disco_release"', html)
print('discog 条目数:', len(entries))
# 找前3个专辑名
titles = re.findall(r'<a class="[^"]*album[^"]*"[^>]*>(.*?)</a>', html)
print('专辑链接数:', len(titles))
if titles:
    print('前3个:', titles[:3])
