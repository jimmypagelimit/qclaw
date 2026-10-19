# V 项目 · 音乐视频背景工具箱

以专辑封面生成 1920×1080 背景，供音乐视频叠加标题、歌词等内容。

## V7 · 深夜唱片内封

2026-10-19 新增静态艺术版本：哑光封套、半露黑胶、细密沟槽、柔和投影和专辑配色环境光。整个背景统一使用专辑主色调，左右采用相同的亮度处理，只保留极轻的对称柔光与细颗粒；封面保持原色，右侧保留叠字空间。无预置标题、歌词或品牌文字。

![V3 与 V7 对比](output/bg_v7/preview/comparison.jpg)

左栏为已有 V3 文件，右栏为 V7。原 V3、V5、V6 均保留。

### 单张

```bash
cd /root/qclaw/tasks/v-project
python3 _gen_batch_bg_v7.py \
  --test 'cover_sources/input/21世纪独立摇滚/Car Seat Headrest - Twin Fantasy.jpg' \
  --output output/bg_v7/preview
```

### 按歌单批量

```bash
python3 _gen_batch_bg_v7.py \
  --input 'cover_sources/input/20世纪华语' \
  --output 'output/bg_v7/20世纪华语'
```

单张默认也写入 `output/bg_v7/`，不写入封面源目录。批量仅处理指定目录的图片，不递归子目录；文件名支持中文和空格。输出为 `bg_v7_序号_原文件名.png`。再次运行同一任务会更新对应 V7 输出，不改旧版本。

大量图片请后台生成并通过文件数确认进度：

```bash
nohup python3 -u _gen_batch_bg_v7.py \
  --input 'cover_sources/input/20世纪华语' \
  --output 'output/bg_v7/20世纪华语' \
  > /tmp/v-project-v7.log 2>&1 &
```

### 环境与验证

系统 Python 3、Pillow 和 NumPy，无新增依赖、网络请求或字体要求。

```bash
python3 -m unittest discover -s tests -p 'test_bg_v7.py' -v
```

像素哈希决定颗粒，跨进程和改名后保持一致（相同运行环境）。封面居中裁方，EXIF 方向先校正，透明封面合成到深灰底。封面在最终画面中占 x=180、y=265、550×550px。露出的唱片最右约 x=1056，叠字建议从 x=1120 起，右侧预留至少 100px 边距。视频标题、歌词应另行合成，不包含在背景 PNG 中。

## 其他版本

| 版本 | 脚本 | 产物 |
| --- | --- | --- |
| V3（内部注释称 V4 精致版） | `_gen_batch_bg_v3.py` | CD 装饰、模糊封面背景，PNG |
| V5 | `_gen_video_bg_v5.py` | 黑胶旋转、EQ 与唱针，MP4 / GIF |
| V6 | `_gen_video_bg_v6.py` | 暗金环境光、频谱残影与 CRT 颗粒，MP4 / GIF |
| V7 | `_gen_batch_bg_v7.py` | 深夜唱片内封，PNG |

V3 已有输出位于 `output/bg_v3/`。V7 样张位于 `output/bg_v7/preview/`。完整记录见 [VERSION_HISTORY.md](VERSION_HISTORY.md)。

## V7 旋转版 · MP4

`_gen_video_bg_v7.py` 复用已确认的统一主色 V7 静态构图。背景、封面、内封和投影不动，仅露出的黑胶纹理及盘标顺时针旋转，高光固定。盘标仅使用抽象线条，不添加虚构专辑信息。

默认 1920×1080、30fps、6秒一圈、无声 H.264 MP4（yuv420p / BT.709 / faststart）。可无缝重复播放，供视频剪辑配乐使用；输出在 `output/video_v7/`。源封面、静态 PNG 和旧动画版本不受影响。

单张：

```bash
python3 _gen_video_bg_v7.py \
  --test 'cover_sources/input/20世纪华语/张雨生-口是心非.jpg' \
  --output output/video_v7/preview
```

按歌单后台量产：

```bash
nohup python3 -u _gen_video_bg_v7.py \
  --input 'cover_sources/input/20世纪华语' \
  --output 'output/video_v7/20世纪华语' \
  > /tmp/v-project-video-v7.log 2>&1 &
```

- `--turn-seconds 6`：每圈秒数，可改为更慢或更快。
- `--loops 1`：完整圈数，例如 `--loops 3` 默认生成18秒视频。
- `--fps 24|30|60`：帧率；帧率乘每圈秒数必须为整数，保证循环周期精确。
- 文件名为 `原封面名_v7.mp4`，支持中文、空格；不递归输入子目录。
- 需要系统 `ffmpeg` 且含 `libx264` 编码器；逐帧流式编码，无需保存大量临时帧。成功后原子替换目标 MP4，失败不替换已有完整视频。

验证命令：

```bash
python3 -m unittest discover -s tests -p 'test*bg_v7.py' -v
```

动画测试核对静止区域、封面像素、可见运动和循环边界。MP4 属于有损视频，编码后的像素会有正常压缩差异。可播放的成品见 `output/video_v7/preview/`。
