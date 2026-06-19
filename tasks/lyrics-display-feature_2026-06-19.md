# 歌词显示功能上线 - 2026-06-19

## 概要
在 album-tracker Web 界面中添加了歌词显示功能。专辑详情弹窗现在在曲目列表下方显示一个独立的歌词区块。

## 修改文件
1. **server.ts** — 新增 `GET /api/albums/:id/lyrics` 端点
   - 按 artist + album_name 匹配 `tasks/lyrics-expert/lyrics/` 下的目录
   - 读取 .txt（纯文本）和 .lrc（时间戳歌词）
   - 按 tracks 表顺序返回
   - 匹配策略：精确匹配 → 前15字符前缀匹配

2. **app.js** — 前端渲染
   - `showAlbumDetail()` 并行请求专辑数据和歌词数据
   - 曲目列表新增歌词标记 📜
   - `renderLyricsBlock()` 渲染独立大块歌词区域
   - `formatLrc()` 解析 LRC 时间戳行，绿色标记时间

3. **style.css** — 歌词样式
   - Cormorant Garamond 衬线字体
   - cream 色底背景，1.9 行距
   - LRC 时间戳绿色斜体标签
   - 可滚动（max-height 600px）
   - 移动端响应式

## 数据
- 238/517 张专辑（46%）匹配到歌词
- 英文歌词主要来自 LRCLIB，中文歌词来自网易云
- 部分专辑有 LRC 时间戳歌词

## 已知问题
- 中文专辑匹配率较低（目录名编码差异）
- `Car Seat Headrest Twin Fantasy` 目录（扁平文件）导致重复条目
- 短文件名匹配可能产生误匹配
