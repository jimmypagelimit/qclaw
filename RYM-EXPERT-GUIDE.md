# RYM 专家能力图谱
> 目标：每天探索 RYM，逐步成为独立音乐领域的 RYM 专家
> 最后更新：2026-06-11

---

## 一、已验证可行的功能

### 1.1 专辑评分抓取 ✅ 稳定使用
- **工具**：`rym_tool.py`（已验证成功106张专辑）
- **数据**：评分/5、评价人数、主流派、封面图URL
- **方法**：CloakBrowser + `link.click()` 绕过 CF，单张50-60秒
- **成功率**：接近100%

### 1.2 流派 Top 10 专辑 ⚠️ 可提取（无评分）
- **已验证**：Indie Rock、Noise Rock、Post-Punk 三个流派页通过 CF
- **数据**：专辑名+艺人+排名
- **特点**：纯 Top 10 预览轮播，无评分
- **用途**：快速了解每流派经典专辑

### 1.3 Charts 排行榜 ✅ 完全可提取
- **验证时间**：2026-06-11（9/10页面通过）
- **数据**：专辑名、艺人、评分/5、评分人数、主流派、发行日期、专辑URL、艺人URL
- **覆盖**：
  - `/charts/top/album/` 全站排行（626KB，抓到38张）
  - `/charts/top/album/2010s/` 年代排行（677KB，抓到38张）
- **规律**：全站页有40个pos，2010s页有约40个pos
- **注意**：需要等CF通过（首页20秒后访问即可）

### 1.4 流派风格树 ✅ 完成
- **已抓取**：Rock 分支 81个子流派（9大类）
- **存储**：`album-tracker/data/rym-rock-style-tree.json`

### 1.5 艺人页 ⚠️ 不稳定
- **Sonic Youth 艺人页**：失败（72644字节=CF固定页）
- **Car Seat Headrest 艺人页**：失败
- **可行时数据**：碟库、相关艺人、简介、侧脸/合作
- **策略**：连续访问多个页面时，CF会随时间通过

---

## 二、关键发现

### CF 行为规律
1. **首页必须**：先访问 `rateyourmusic.com`，等待20秒
2. **单次 launch**：一次 launch 后可顺序访问多个页面（不重试launch）
3. **文件大小判断**：`72644字节` = CF 拦截页，可用此判断是否成功
4. **流派页规律**：`/genre/{slug}/` 格式的页面更稳定通过 CF
5. **搜索页**：`/search?search-type=albums` 目前被完全拦截
6. **艺人页**：最不稳定，成功率约30-40%

### Charts HTML 结构（用于提取）
```html
<div id="pos1" class="page_section_charts_item_wrapper">
  <a class="page_charts_section_charts_item_link release" href="/release/album/...">
    <span class="ui_name_locale_original">Album Title</span>
  </a>
  <a class="artist" href="/artist/...">
    <span class="ui_name_locale_original">Artist Name</span>
  </a>
  <span class="page_charts_section_charts_item_details_average_num">4.38</span>
  <span class="page_charts_section_charts_item_stats compact">
    <span class="abbr">106k</span>  <!-- 评分数量 -->
  </span>
  <div class="page_charts_section_charts_item_genres_primary">
    <a class="genre">Genre Name</a>
  </div>
</div>
```

### Charts Top 20 (All-Time) 关键数据
| # | 评分 | 数量 | 艺人 | 专辑 |
|---|------|------|------|------|
| 1 | 4.38 | 106k | Kendrick Lamar | To Pimp a Butterfly |
| 2 | 4.30 | 134k | Radiohead | OK Computer |
| 3 | 4.33 | 104k | Radiohead | In Rainbows |
| 4 | 4.37 | 93k | Pink Floyd | Wish You Were Here |
| 5 | 4.33 | 86k | King Crimson | In the Court of the Crimson King |
| 6 | 4.33 | 88k | Kendrick Lamar | Good Kid, M.A.A.D City |
| 7 | 4.25 | 108k | Radiohead | Kid A |
| 8 | 4.27 | 105k | Pink Floyd | The Dark Side of the Moon |
| 9 | 4.33 | 79k | Madvillain | Madvillainy |
| 10 | 4.25 | 95k | My Bloody Valentine | Loveless |
| 11 | 4.30 | 84k | The Beatles | Abbey Road |
| 12 | 4.26 | 70k | Talking Heads | Remain in Light |
| 13 | 4.26 | 72k | David Bowie | The Rise and Fall of Ziggy Stardust |
| 15 | 4.27 | 64k | Nas | Illmatic |
| 16 | 4.23 | 79k | The Beatles | Revolver |
| 17 | 4.24 | 68k | Black Sabbath | Paranoid |

---

## 三、待探索功能

| 功能 | 价值 | 可行性 | 备注 |
|------|------|--------|------|
| 相似艺人推荐 | ⭐⭐⭐ | ⚠️ 待验证 | 需要艺人页通过CF |
| Pop/Folk/Metal 流派树 | ⭐⭐ | 🎯 下一步 | 方法同Rock |
| 发片日历 | ⭐⭐ | ⚠️ CF不稳定 | 追踪新专辑 |
| 用户列表 | ⭐⭐ | ❓ 未测试 | 社区榜单发现 |
| 厂牌发现 | ⭐ | 🎯 可行 | 同厂牌艺人推荐 |
| 艺人关系网络 | ⭐⭐⭐ | ⚠️ 待验证 | 侧脸/合作 |

---

## 四、每日探索计划

### 每天必做
- [x] 用 `rym_tool.py` 抓取用户未收录专辑评分
- [x] 验证流派页 CF 通过率
- [x] 验证 Charts 页面数据提取

### 每日探索节奏（每次 heartbeat 执行一项）
1. **RYM 功能探索**：检查新页面类型（流派/艺人/Charts/用户页）
2. **音乐发现**：从 Charts Top 找用户缺失的专辑
3. **流派研究**：深入一个子流派页面
4. **相似艺人**：尝试找1个用户收藏艺人的相似艺人

### 每周目标
- [ ] 抓取 1 个完整流派 Chart Top 50
- [ ] 爬取 Pop/Folk/Metal 其一的流派树
- [ ] 找 5 个相似艺人

---

## 五、技术工具箱（更新于 2026-07-20）

### 方案 A：Selenium + Firefox profile（推荐 🏆）

```python
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

opts = Options()
opts.add_argument("-profile")
opts.add_argument("/root/.mozilla/firefox/3pdxe3s8.default-esr")
driver = webdriver.Firefox(options=opts)
driver.get("https://rateyourmusic.com/charts/top/album/all-time/")

# 提取数据
import re
html = driver.page_source
alts = re.findall(r'alt="([^"]* - [^"]*)"', html)
ratings = re.findall(r'class="page_charts_section_charts_item_details_average_num"[^>]*>([^<]+)<', html)
driver.quit()
```

- **速度**：秒级（无需等待 CF）
- **依赖**：geckodriver v0.37.0 + selenium
- **限制**：cf_clearance 有有效期；profile 不能同时被多个 Firefox 进程使用

### 方案 B：computer_use + 真实 Firefox

```python
# 启动 Firefox
DISPLAY=:0 firefox-esr --new-window https://rateyourmusic.com/

# 用 computer_use capture 查看页面
# 点击 CF 验证复选框
# 通过后用键盘快捷键导航
```

- **速度**：慢（每次操作需截屏），适合"开门"场景
- **依赖**：cua-driver 需要 DISPLAY=:0 + AT-SPI 无障碍服务

### 方案 C：CloakBrowser（旧方案）

```python
from cloakbrowser import launch
import time

ctx = launch(headless=False)
page = ctx.new_page()

# 1. 首页等CF
page.goto('https://rateyourmusic.com/')
time.sleep(20)

# 2. 之后顺序访问多个目标页
```

- **问题**：free tier（v146）已被 CF 识别，需要 Pro 版
- **速度**：单张专辑 50-60 秒

### 启动脚本（单次 launch 访问多页）
```python
from cloakbrowser import launch
import time

ctx = launch(headless=False)
page = ctx.new_page()

# 1. 首页等CF
page.goto('https://rateyourmusic.com/')
time.sleep(20)

# 2. 之后顺序访问多个目标页
pages = [
    ('https://rateyourmusic.com/charts/top/album/', 'charts_top'),
    ('https://rateyourmusic.com/charts/top/album/2010s/', 'charts_2010s'),
    ('https://rateyourmusic.com/genre/noise-rock/', 'genre_noise_rock'),
    ('https://rateyourmusic.com/genre/shoegaze/', 'genre_shoegaze'),
]
for url, name in pages:
    page.goto(url)
    time.sleep(12)  # 等待加载
    content = page.content()
    if len(content) > 100000:  # 判断CF通过
        with open(f'{name}.html', 'w', encoding='utf-8') as f:
            f.write(content)
        page.screenshot(path=f'{name}.png')

ctx.close()
```

### Charts 数据提取正则
```python
# 分割每个 chart item
pos_pattern = re.compile(
    r'<div id="pos(\d+)"[^>]*>(.*?)(?=<div id="pos\d+"|\Z)', re.DOTALL)

for m in pos_pattern.finditer(content):
    rank = m.group(1)
    block = m.group(2)
    
    # 评分
    rating = re.search(r'class="page_charts_section_charts_item_details_average_num">(\d\.\d{2})</span>', block)
    
    # 评分数量
    stats = re.search(r'class="page_charts_section_charts_item_stats compact">(.*?)</div>', block, re.DOTALL)
    count = re.search(r'class="abbr">\s*(\S+)\s*</span>', stats.group(1)) if stats else None
    
    # 专辑名
    album = re.search(r'<a[^>]+class="[^"]*release[^"]*"[^>]*>.*?<span class="ui_name_locale_original">([^<]+)</span>', block, re.DOTALL)
    
    # 艺人
    artist = re.search(r'<a[^>]+class="[^"]*artist[^"]*"[^>]*>.*?<span class="ui_name_locale_original">([^<]+)</span>', block, re.DOTALL)
    
    # 流派
    genres = re.findall(r'class="page_charts_section_charts_item_genres_primary".*?<a[^>]+>([^<]+)</a>', block, re.DOTALL)
```

### 数据文件位置
- Charts 原始HTML：`rym_explore/charts_top.html` (626KB) / `charts_2010s.html` (677KB)
- Charts 结构化数据：`rym_explore/chart_data.json`
- 流派页HTML：`rym_explore/genre_*.html`
- Rock 流派树：`album-tracker/data/rym-rock-style-tree.json`

---

_探索进度：2026-06-11 系统测试完成，开始日常探索_
