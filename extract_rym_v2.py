# 更精确的 RYM 数据提取
import re

with open('C:/Users/qujt/.qclaw/workspace/rym_album_click.html', 'r', encoding='utf-8') as f:
    html = f.read()

print("=== Paul McCartney - The Boys of Dungeon Lane (RYM) ===")
print()

# 方法1: 找 avg_rating 类后面的文本
m = re.search(r'class="avg_rating"[^>]*>([\d.]+)', html)
if m:
    print(f"RYM 评分: {m.group(1)} / 5")

# 方法2: 找 "Ratings" 前面的数字
m = re.search(r'([\d,]+)\s*Ratings?', html)
if m:
    print(f"评价数: {m.group(1)}")

m = re.search(r'([\d,]+)\s*Reviews?', html)
if m:
    print(f"评论数: {m.group(1)}")

# 年份 - 从页面标题或内容
m = re.search(r'(\d{4})\s*\)', html[:5000])
if m:
    print(f"年份: {m.group(1)}")

# 流派 - 用更宽松的模式
genres = re.findall(r'href="/genre/[^"]+">([^<]+)</a>', html)
if genres:
    ug = list(dict.fromkeys(genres))
    # 过滤掉非流派
    real_genres = [g for g in ug if g not in ('sign in', 'more', 'all') and len(g) > 2]
    if real_genres:
        print(f"流派: {', '.join(real_genres[:8])}")

# 风格
styles = re.findall(r'href="/style/[^"]+">([^<]+)</a>', html)
if styles:
    us = list(dict.fromkeys(styles))
    real_styles = [s for s in us if s not in ('sign in', 'more', 'all') and len(s) > 2]
    if real_styles:
        print(f"风格: {', '.join(real_styles[:8])}")

# 发行信息区域
print()
print("=== 发行信息 ===")
# 查找 album_info 表格
info_section = re.search(r'class="album_info[^"]*"(.*?)</table>', html, re.DOTALL | re.IGNORECASE)
if info_section:
    info_text = info_section.group(1)
    # 提取所有 label-value 对
    rows = re.findall(r'<td[^>]*>\s*(\w[\w\s]*?)\s*</td>\s*<td[^>]*>(.*?)</td>', info_text, re.DOTALL)
    for label, value in rows:
        clean_label = re.sub(r'<[^>]+>', '', label).strip()
        clean_value = re.sub(r'<[^>]+>', '', value).strip()
        if clean_label and clean_value:
            print(f"{clean_label}: {clean_value}")
else:
    # 尝试另一种格式
    for pattern_name, pattern in [
        ("Label", r'(?:Label|label)[^<]*</td>\s*<td[^>]*>([^<]+)'),
        ("Country", r'(?:Country|country)[^<]*</td>\s*<td[^>]*>([^<]+)'),
        ("Format", r'(?:Format|format)[^<]*</td>\s*<td[^>]*>([^<]+)'),
    ]:
        m = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
        if m:
            print(f"{pattern_name}: {m.group(1).strip()}")

# 统计数据
print()
print("=== 统计概览 ===")
for name, pat in [
    ("拥有数", r'(\d[\d,]*)\s*(?:have|own|in catalog|collections?)'),
    ("愿望单", r'(\d[\d,]*)\s*(?:want|wishlist)'),
]:
    m = re.search(pat, html, re.IGNORECASE)
    if m:
        print(f"{name}: {m.group(1)}")
