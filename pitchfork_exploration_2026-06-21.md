# Pitchfork 网站探索报告

## 探索时间
2026-06-21 01:16 (Asia/Shanghai)

## 目标
探索 Pitchfork 当前网站结构，确认评论、评分、搜索、RSS 的可访问性及数据提取方式，为专辑追踪器项目补充评分/评论来源。

## 关键发现

### 1. 整体可访问性
- 主站 `https://pitchfork.com` 可正常访问，无 Cloudflare 拦截
- RSS 源 `https://pitchfork.com/feed/rss` 稳定返回 XML
- 搜索页 `https://pitchfork.com/search/?query=XXX` 可用

### 2. 评论页面结构
- URL 模式：`/reviews/albums/{artist-slug}-{album-slug}/`
- 示例：
  - `https://pitchfork.com/reviews/albums/miles-davis-miles-56-the-prestige-recordings/`
  - `https://pitchfork.com/reviews/albums/oneohtrix-point-never-tranquilizer/`
- 页面包含：标题、作者、摘要、正文、评分、Best New 标签、封面图

### 3. 评分提取方式（更新）
- **旧方式**：JSON-LD 中的 `reviewRating.ratingValue` 已失效
- **当前有效方式**：页面 HTML 中搜索 `"score": X.X`（正则）
- 实测：
  - Oneohtrix Point Never - Tranquilizer: **8.6**
  - Addison Rae - Addison: **8**
  - Rosalía - LUX: **8.6**
- 注意：页面中的 `CircularRating` 显示 `0.0` 是**读者评分**（未评分），不是编辑评分

### 4. 搜索功能
- URL：`https://pitchfork.com/search/?query={encoded_query}`
- 返回 HTML 中包含 `/reviews/albums/...` 链接
- 可直接用于专辑搜索和 URL 发现
- 测试查询：
  - Car Seat Headrest → 找到 `teen-of-denial-joes-story`、`the-scholars`、`making-a-door-less-open`
  - Sonic Youth → 找到多张专辑
  - Twin Fantasy → 找到 `car-seat-headrest-twin-fantasy`

### 5. Best New Music 页面
- URL：`https://pitchfork.com/best/`
- 包含 Best New Album、Best New Reissue、Best New Track
- 无具体数值排名，只有入选标识

### 6. RSS 源
- 地址：`https://pitchfork.com/feed/rss`
- 包含新闻、评论、分类标签、缩略图、作者
- 适合监控最新内容，不适合回溯历史评分

## 数据提取建议

### 单张专辑查询流程
1. 访问 `https://pitchfork.com/search/?query={artist}+{album}`
2. 从 HTML 中提取 `/reviews/albums/...` 链接
3. 访问评论页，用正则 `"score":\s*(\d+\.?\d*)` 提取评分
4. 检查页面中是否包含 `Best New Album` / `Best New Reissue` / `Best New Track` 字符串
5. 提取作者、发布日期、摘要

### 注意事项
- 评分是编辑评分，不是读者评分（不要误提取 `0.0`）
- 部分页面可能没有评分（预热文章或未评分）
- BNM 标签在导航中也可能出现，需要限定在评论主体区域判断
- 评论正文可用 readability 提取，但需过滤外部内容提示

## 与现有项目集成

-  album-tracker 项目已有 `pitchfork_score` 字段
- 可新增一个轻量级 Pitchfork 查询脚本：`pf_query.py "artist" "album"`
- 输出：评分、BNM 标签、评论 URL、摘要
- 不需要浏览器自动化，直接 urllib 即可

## 限制
- 只能获取 Pitchfork 已评论的专辑
- 无批量 API，需逐张搜索
- 评分不包含小数位精度（如 8 不是 8.0）
- 不提供曲目列表、时长、厂牌等元数据

## 下一步建议
1. 编写 `pf_query.py` 单专辑查询脚本
2. 测试数据库中已有专辑的 Pitchfork 匹配率
3. 批量补填缺失的 Pitchfork 评分（从数据库中 20 张已有开始扩展）

---
依据：
- Pitchfork 首页：https://pitchfork.com
- Pitchfork RSS：https://pitchfork.com/feed/rss
- Pitchfork 评论页示例：https://pitchfork.com/reviews/albums/oneohtrix-point-never-tranquilizer/
- Pitchfork 搜索页：https://pitchfork.com/search/?query=Car+Seat+Headrest
