# RYM Rock Style Tree 抓取完成

## 目标
从 RYM (RateYourMusic.com) 抓取完整的 Rock 流派树形结构

## 执行过程

### 1. Genres 首页抓取（失败→部分成功）
- 用 CloakBrowser 绕过 CF，访问 `/genre/` 页面
- 发现页面是折叠卡片式布局（每个流派一个卡片），不是完整树形
- 点击展开所有折叠节点，获取 2776 个唯一流派链接
- **问题**: `<li>` 嵌套深度计算错误（3MB HTML 中 `<li>` 标签太多）
- **问题**: `img alt` 属性存的是专辑封面名（如 "Kendrick Lamar - To Pimp a Butterfly"），不是流派名
- **解决**: 改用链接文本内容（`<a>genre_name</a>`）作为流派名

### 2. /genre/rock/ 页面抓取（成功✅）
- 直接访问 `https://rateyourmusic.com/genre/rock/`
- 页面 494KB HTML，包含完整的 Rock 子流派列表
- 提取到 **81 个 Rock 子流派**
- 尝试点击 "Expand Hierarchy" 按钮（数量不变，说明页面已列出全部）

### 3. 结果整理
- 81 个子流派按音乐学脉络整理为 **9 大分支**:
  1. Rock & Roll / Early Rock (3)
  2. Garage / Punk (5)
  3. Indie / Alternative (6)
  4. Folk Rock (7)
  5. Psychedelic / Progressive / Art (13) — 最大分支
  6. Hard / Heavy (11)
  7. Glam / Pop / Soft (13)
  8. Industrial / Electronic (3)
  9. Regional / World Rock (18) — 最多样

## 关键技术发现
- RYM Genres 首页 (`/genre/`) 是流派目录（卡片式），不是树形视图
- 单个流派页面 (`/genre/rock/`) 列出该流派的全部直接子流派
- 链接文本 = 流派名，`img alt` = 专辑封面描述（不要用！）
- CloakBrowser `headless=False` + JS `window.location.href` 导航可绕过 CF

## 输出文件
- `_rym_rock_genre.html` — RYM Rock 页面完整 HTML (494KB)
- `_rym_rock_genre.png` — 页面截图
- `_rym_rock_hierarchy.png` — 展开后截图 (41838px 高)
- `_rym_rock_subgenres.json` — 81 个子流派原始数据
- `_rym_rock_tree_final.json` — 整理后的树形结构 JSON
- `_rym_full_genre_tree.json` — 全部 34 个顶级流派（Genres 首页数据）

## 下一步可选
- 将 81 个 Rock 子流派写入数据库 styles 表
- 用此树补全现有专辑的 style 字段
- 抓取其他顶级流派（Metal、Punk、Pop 等）的子树