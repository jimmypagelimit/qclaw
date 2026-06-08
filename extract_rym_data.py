# 提取 RYM 专辑数据
import re

with open('C:/Users/qujt/.qclaw/workspace/rym_album_click.html', 'r', encoding='utf-8') as f:
    html = f.read()

print("=== RYM 精确数据提取 ===")
print()

# 评分
patterns = [
    (r'avg_rating[^>]*>([\d.]+)', 'avg_rating'),
    (r'"avgRating":\s*([\d.]+)', 'avgRating JSON'),
    (r'([\d.]{2,3})\s*</span>\s*<span[^>]*>.*?/ 5', 'span /5'),
]
for p, label in patterns:
    m = re.search(p, html)
    if m:
        print(f"评分: {m.group(1)} ({label})")
        break

# 评价数
m = re.search(r'([\d,]+)\s*Ratings?', html)
if m: print(f"评价数: {m.group(1)}")

m = re.search(r'([\d,]+)\s*Reviews?', html)
if m: print(f"评论数: {m.group(1)}")

# 年份
for p in [r'(\d{4})\s*</a>\s*\)', r'year.*?(\d{4})']:
    m = re.search(p, html, re.IGNORECASE | re.DOTALL)
    if m:
        print(f"年份: {m.group(1)}")
        break

# 流派
genres = re.findall(r'<a href="/genre/[^"]+"[^>]*>([^<]+)</a>', html)
if genres:
    ug = list(dict.fromkeys(genres))[:10]
    print(f"流派: {', '.join(ug)}")

# 风格
styles = re.findall(r'<a href="/style/[^"]+"[^>]*>([^<]+)</a>', html)
if styles:
    us = list(dict.fromkeys(styles))[:10]
    print(f"风格: {', '.join(us)}")

# 厂牌
labels = re.findall(r'label.*?<a href="[^"]+"[^>]*>([^<]+)</a>', html, re.IGNORECASE | re.DOTALL)
if labels:
    print(f"厂牌: {labels[0].strip()}")

# 发行格式
for fmt in ['CD', 'Vinyl', 'Digital', 'Cassette', 'LP']:
    if fmt in html:
        print(f"格式: {fmt}")
        break

# 找评分区域上下文
idx = html.find('avg_rating')
if idx > 0:
    print()
    print("=== 评分区域HTML片段 ===")
    print(html[max(0,idx-100):idx+300])
