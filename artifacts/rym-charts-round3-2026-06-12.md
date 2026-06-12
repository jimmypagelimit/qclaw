# RYM 深化 Round 3 — 时间：2026-06-12 下午

## 完成内容

### 1. 新发片抓取（/new-music/）
- **24 张专辑**，成功提取：专辑名、艺人、评分、评价数、wishlist、发布日期、流派、封面 URL
- 覆盖 Boards of Canada、Converge、Panopticon、Swans、Paul McCartney 等
- 知识库：`tasks/rym-expert/docs/NEW-RELEASES-KB.md`

### 2. 年度 Charts 抓取（2020-2025）
- **233 条**（每年 37-40 条）
- 成功提取：专辑名、艺人、评分、评价数、发布日期、流派、RYM URL
- 数据文件：
  - `data/charts-yearly/master_yearly_20260612.json`
  - `data/charts-yearly/{2020,2021,2022,2023,2024,2025}/{year}.json`
  - `data/charts-yearly/2025.json`（根目录）

### 3. 收藏差距分析
- 高分缺失专辑（4.0+）：6 张
  1. Magdalena Bay - Imaginal Disk（4.1）2024
  2. Black Country, New Road - Ants From Up There（4.04）2022
  3. JID - The Forever Story（4.01）2022
  4. Natalia Lafourcade - De todas las flores（4.0）2022
  5. JPEGMAFIA - LP!（4.0）2021
  6. 青葉市子 - アダンの風（4.0）2020

### 4. 技术成果
- **CloakBrowser 成功绕过 CF**：首页等 25 秒后 JS `location.href` 导航全通
- **正则提取模板固定**：
  - 新发片：`release_` ID 窗口法
  - Charts：`object_release` 块分割法
- **RYM Charts HTML 结构**：
  - 评分：`details_average_num`
  - 评价数：`details_ratings`
  - 专辑名/艺人：`<span class="ui_name_locale_original">`
  - 流派：`genre comma_separated`

## Git 提交
- `e6ee080` — Round 3: RYM yearly charts + new releases + KB（15 files, 8056 inserts）

## 待办
- [ ] 6 张高分缺失专辑是否入库决策
- [ ] Pitchfork/AOTY 深化（推迟）
- [ ] 更多流派树爬取（Metal/Folk/Electronic）
- [ ] 系统化艺人碟库抓取