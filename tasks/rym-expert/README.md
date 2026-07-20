# RYM Expert 项目

> 深化增强版 RYM 抓取能力
> 最后更新：2026-07-20

## 项目结构

```
tasks/rym-expert/
├── rym_cli.py           # 统一 CLI 工具
├── rym_db_bridge.py     # 数据库回填管道
├── rym_kb_builder.py    # 知识库生成器
├── data/
│   ├── charts-yearly/   # 年度榜单数据
│   ├── collection/      # 收藏对比数据
│   └── new-releases/    # 新发片数据
├── docs/
│   └── RYM-KB.md        # RYM 知识库
└── README.md
```

## 已实现功能

### 1. 专辑搜索 ✅
基于 `rym_tool.py`（CloakBrowser + JS click 绕 CF）
- 单张专辑搜索：`python rym_tool.py "专辑名" "艺人名"`
- 输出：JSON + 截图

### 2. Charts 排行榜抓取 ✅（2026-07-20 新增 Selenium 方案）
- **工具**：Selenium + geckodriver + Firefox profile
- **数据**：专辑名、艺人、评分/5、评分人数
- **速度**：秒级（比 CloakBrowser 快 10 倍）
- **输出**：`/tmp/rym_charts.json`（结构化 JSON）

### 3. 数据库回填 ⚡
- 目标：`_music_latest.db`
- 字段：`rym_rating`, `rym_ratings_count`, `rym_url`
- 覆盖率：101/520（19.4%）

### 4. 知识库生成 📚
- `docs/RYM-KB.md` — RYM 高分榜 Top 50
- 自动统计覆盖率

### 5. 数据积累 📊
- 年度榜单：2020-2025（约 300+ 条）
- 新发片监控
- 收藏对比分析

## 待实现功能

### 1. 流派树爬取 🌳
- 入口：`/genre/{slug}/`
- 目标：Metal/Folk/Electronic 等
- 已知问题：子流派区域定位失败

### 2. Charts 自动化 📈
- cron 任务：每 3 小时抓取
- 增量更新

### 3. 艺人碟库 🎸
- 收藏对比推荐
- 缺失高分专辑推荐

## CF 绕过方案（2026-07-20 定稿）

### 核心流程：computer_use 开门 → Selenium 抓数据

```
┌─────────────────────────────────────────────────────────┐
│  步骤 1: computer_use + 真实 Firefox                    │
│  → 启动 Firefox，导航到 RYM                              │
│  → 点击 CF 验证复选框（真人操作，CF 不拦）                │
│  → 关闭 Firefox（cf_clearance 已写入 profile）           │
│  └────────── 这一步只需几秒，偶尔执行一次 ──────────────┘
│                              ↓
│  ┌─────────────────────────────────────────────────────┐ │
│  │ 步骤 2: Selenium + Firefox profile（复用 cookie）   │ │
│  │ → 启动 headless Firefox，用已有 profile              │ │
│  │ → 直接访问任意 RYM 页面（CF 已通过）                  │ │
│  │ → 提取数据，关闭浏览器                               │ │
│  │ └────────── 这一步秒级完成，可反复执行 ────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 方案 A：Selenium + Firefox profile（主力 ⭐）

```python
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

opts = Options()
opts.add_argument("-profile")
opts.add_argument("/root/.mozilla/firefox/3pdxe3s8.default-esr")
driver = webdriver.Firefox(options=opts)
driver.get("https://rateyourmusic.com/charts/top/album/all-time/")
# CF 已通过，直接提取数据
```
- **原理**：复用 Firefox profile 中的 cf_clearance cookie
- **速度**：秒级，无需等待 CF 挑战
- **依赖**：`geckodriver`（v0.37.0）+ `selenium`
- **限制**：cf_clearance 有有效期（通常几小时到几天），过期后用 computer_use 重新开门

### 方案 B：computer_use + 真实 Firefox（开门专用 🚪）

- **用途**：用来通过 CF 验证，生成有效的 cf_clearance cookie
- **流程**：启动 Firefox → 访问 RYM → 点击 CF 复选框 → 关闭
- **速度**：慢但只做一次，后续用 Selenium 快速抓取
- **cua-driver 配置**：需在 systemd 服务中设置 DISPLAY=:0

### ~~方案 C：CloakBrowser（已废弃）~~

- ~~free tier 被 CF 识别，Pro 版 $19/月~~
- ~~不再使用，所有需求由 computer_use + Selenium 替代~~

## 关键发现（2026-07-20）

### cf_clearance 绑定浏览器指纹
- Cloudflare 的 `cf_clearance` cookie **绑定到签发时的 TLS 指纹**
- 导出 cookie 后用 curl/requests/curl_cffi 请求 → 403（指纹不匹配）
- 即使 curl_cffi 模拟 Firefox 133/144/147 也不行
- **唯一可行方案**：复用同一个浏览器上下文（profile）

### Firefox 远程调试限制
- `--remote-debugging-port 9222` 在 Firefox ESR 上不支持 Chrome 的 CDP `/json` 端点
- Firefox 的远程调试协议与 Chrome 不同，需要特殊处理
- 推荐使用 Selenium + geckodriver 代替

### Selenium 环境搭建
```bash
# 安装 geckodriver（需匹配 Firefox 版本）
# Firefox ESR 140 → geckodriver 0.37.0
curl -L -o /tmp/gd.tar.gz "https://github.com/mozilla/geckodriver/releases/download/v0.37.0/geckodriver-v0.37.0-linux64.tar.gz"
tar xzf /tmp/gd.tar.gz -C /usr/local/bin/

# 安装 selenium
pip3 install --break-system-packages --ignore-installed selenium

# 使用已有 Firefox profile 启动
python3 -c "
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
opts = Options()
opts.add_argument('-profile')
opts.add_argument('/root/.mozilla/firefox/3pdxe3s8.default-esr')
driver = webdriver.Firefox(options=opts)
driver.get('https://rateyourmusic.com/')
print(driver.title)  # 应显示 Welcome! - Rate Your Music
driver.quit()
"
```

## 技术约束（更新于 2026-07-20）

1. ~~CloakBrowser 必须~~ → **Selenium + Firefox profile 更优**
2. ~~headless=False~~ → **Selenium 支持 headless 模式**
3. ~~首页等待 20-30 秒~~ → **复用 profile 无需等待 CF**
4. **cf_clearance 有有效期**：过期后需重新用真实 Firefox 过 CF
5. **Firefox profile 不能同时被多个进程使用**：Selenium 和 GUI Firefox 不能同时开
6. **cua-driver 需要 DISPLAY=:0**：在 systemd 服务中需配置 Environment

## 快速开始

```bash
# 搜索专辑（CloakBrowser）
python rym_tool.py "Twin Fantasy" "Car Seat Headrest"

# 抓取 Charts（Selenium，推荐）
python rym_cli.py charts

# 回填数据库（前50张）
python rym_db_bridge.py --limit 50

# 生成知识库
python rym_kb_builder.py
```

## 参考资料

- [TOOLS.md](../../TOOLS.md) — 技术细节
- [PLAN.md](PLAN.md) — 深化计划
- [RYM-EXPERT-GUIDE.md](../../RYM-EXPERT-GUIDE.md) — 能力图谱
