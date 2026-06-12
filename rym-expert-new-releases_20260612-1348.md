# RYM 发片日历探索 — 2026-06-12

## 目标
推进 RYM Expert 尚未完成的能力：发片日历提取

## 结果
✅ 成功提取 RYM /new-music/ 页面，10条新发片，100%有评分

## 关键发现
- RYM 新发片页默认展示10条（可能支持翻页）
- 完整字段：艺人/专辑/评分/评价数/想听数/发行日期/流派/封面URL
- HTML结构：`newreleases_itembox` → `newreleases_item_title` + `newreleases_item_artist` + 三个stat span

## 本轮亮点新碟
1. Boards of Canada - Inferno [3.91] — Downtempo
2. Panopticon - Det hjemsøkte hjertet [3.83] — Atmospheric Black Metal
3. Converge - Hum of Hurt [3.73] — Metalcore

## 用户口味匹配 (Indie/Metal/Punk)
Panopticon, Converge, Genesis Owusu (Post-Punk Revival)

## 脚本
`scripts/extract_new_releases_v5.py`（5版迭代，最终稳定）

## 教训
- page.evaluate 导航后执行上下文销毁是正常的，需要 try/except + sleep
- 评分在 `newreleases_avg_rating_stat` span 里，正则 `newreleases_avg_rating_stat">([\d.]+)</span>`
- Windows GBK 编码：输出必须写文件，不能 print
