# V 项目 — 视频制作工具箱

## 项目定位
音乐视频背景图批量生成 + 视频合成工具箱。当前阶段：背景图生成完成，视频合成待启动。

## 目录结构

```
tasks/v-project/
├── README.md               ← 本文件
├── _gen_batch_bg.py        ← CD风格背景图生成脚本
├── cover_sources/          ← 封面源图（软链/指向，非实际存储）
└── output/                 ← 输出产物目录
    ├── bg/                 ← 背景图输出（PNG, 1920×1080）
    └── video/              ← 视频合成产物（待开发）
```

## 已完成
**2026-05-23 — CD风格背景图生成（20张）**
- 歌单：NME C86 20世纪独立摇滚
- 输入：`video_thumbs/20th_century_indie/`（20张封面）
- 输出：`video_thumbs/20th_century_indie_bg/`（20张PNG）
- Git commit: `ff669b1` / `9a94a49`

## CD风格参数（敲定版）
| 参数 | 值 |
|------|-----|
| 尺寸 | 1920×1080 (16:9) |
| 封面位置 | 左侧180px，垂直居中 |
| 封面尺寸 | 550px |
| 模糊背景 | GaussianBlur radius=30 |
| 暗角 | vignette 强度0.75 |
| CD外圈 | 深色边框16px + 细线 #3C3240 |
| CD内圈 | 圆环 inner_r=55, hole_r=14 |
| 镜面高光 | 左上角弧形白带 |
| 右侧渐暗 | fade_x = 封面右边缘 + 80px |
| 右上装饰 | 三颗金色小圆点 |
| 封面边框 | 金色分隔线 |

## 待开发
- [ ] 视频合成（背景图 + 音乐片段 + 文字→MP4）
- [ ] 多歌单支持（非C86系列）
- [ ] 封面自动下载流程整合
- [ ] 文字（歌名/艺人/评论）渲染

## 快速命令
```bash
# 生成背景图
C:\Python311\python.exe tasks\v-project\_gen_batch_bg.py

# 输入封面放在
tasks\v-project\cover_sources\input\    # 或指定目录

# 输出在
tasks\v-project\output\bg\
```
