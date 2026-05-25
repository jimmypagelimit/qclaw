# 张悬专辑统一完成 - 2026-05-23 12:08

## 任务目标
统一张悬专辑的 artist 字段和 cover_image_url 字段，去除繁体和 `[Deserts Chang]` 后缀。

## 执行步骤

### 1. 检查初始状态
- albums 总表：4 条张悬专辑，无繁体残留 ✅
- albums_2026 表：2 条张悬专辑，artist=`张悬 [Deserts Chang]`（带后缀），cover_image_url 指向繁体文件名 ❌

### 2. 执行统一脚本（do_zx_unify_v2.py）
- 更新 albums_2026 表 artist 字段：`张悬 [Deserts Chang]` → `张悬`
- 更新 albums_2026 表 cover_image_url：繁体文件名 → 简体文件名
  - id=39（城市）：`covers/448-張懸_...jpg` → `covers/168-张悬-城市.jpg`
  - id=40（神的游戏）：`covers/449-張懸_...jpg` → `covers/6-张悬-神的游戏.jpg`
- 删除繁体封面文件（不存在，已跳过）

### 3. 验证结果（verify_zx.py）
- albums_2026 表：artist 均为 `张悬`，cover_image_url 均为简体文件名 ✅
- 数据库无繁体残留（artist/album_name/cover_image_url 字段均为 0 条）✅
- 封面文件无繁体残留 ✅

## 关键发现

1. **封面文件位置错误**：之前一直检查 `G:\原创计划\covers\`，实际在 `album-tracker/covers/` 目录下
2. **繁体封面文件已不存在**：可能之前已被删除
3. **数据库更新需要 conn.commit()**：否则更改不会保存

## 最终状态

- albums 总表：4 条张悬专辑，artist=`张悬`，无繁体，无重复 ✅
- albums_2026 表：2 条张悬专辑，artist=`张悬`，cover_image_url 为简体文件名 ✅
- 封面文件：484 张，无繁体残留 ✅

## 下一步

- 可以开始中午的批量入库
- 准备批量导入的专辑列表（CSV 或 Markdown）
- 先搜索一遍，记录已存在的专辑 ID
- 停止 Web 服务（避免数据库锁）
- 批量新增专辑（CLI 循环）
- 批量下载封面
- 验证封面文件
- 重启 Web 服务
- 提交到 git

---
*Task completed at: 2026-05-23 12:08*
