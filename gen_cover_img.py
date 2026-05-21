from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

# 路径
cover_path = r'C:\Users\15206\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\covers\323-COV.jpg'
output_path = r'C:\Users\15206\.qclaw\workspace\Twin_Fantasy_cover.png'

W, H = 1920, 1080

# 1. 打开封面
cover = Image.open(cover_path).convert('RGB')

# 2. 创建画布，模糊封面作背景
bg = cover.resize((W + 200, H + 200)).crop((0, 0, W, H))
bg = bg.filter(ImageFilter.GaussianBlur(radius=60))
# 加暗层
overlay = Image.new('RGB', (W, H), (10, 10, 30))
bg = Image.blend(bg, overlay, alpha=0.55)

# 3. 左侧封面
cover_size = 520
cover_square = cover.resize((cover_size, cover_size), Image.LANCZOS)
# 圆角
mask = Image.new('L', (cover_size, cover_size), 0)
from PIL import ImageDraw
dm = ImageDraw.Draw(mask)
dm.rounded_rectangle([0, 0, cover_size, cover_size], radius=24, fill=255)
bg.paste(cover_square, (80, (H - cover_size) // 2), mask)

# 4. 右侧文字
draw = ImageDraw.Draw(bg)

# 尝试加载字体，fallback
def get_font(size):
    paths = [
        'C:/Windows/Fonts/msyhbd.ttc',   # 微软雅黑粗体
        'C:/Windows/Fonts/msyh.ttc',      # 微软雅黑
        'C:/Windows/Fonts/simhei.ttf',    # 黑体
        'C:/Windows/Fonts/arial.ttf',     # Arial
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except:
                continue
    return ImageFont.load_default()

font_rank   = get_font(180)
font_np     = get_font(26)
font_title  = get_font(68)
font_artist = get_font(38)
font_meta   = get_font(22)
font_mv     = get_font(30)
font_tag    = get_font(24)

# 右侧区域
right_x = 80 + cover_size + 80   # 680
right_w = W - right_x - 80        # 1160

# #1 排名（大字背景）
rank_text = "#1"
bbox = draw.textbbox((0, 0), rank_text, font=font_rank)
rw = bbox[2] - bbox[0]
draw.text((right_x, 60), rank_text, font=font_rank, fill=(255, 255, 255, 30))

# 正在播放
np_text = "▶  正在播放：Twin Fantasy"
draw.text((right_x, 240), np_text, font=font_np, fill='#1DB954')

# 专辑名
title = "Twin Fantasy"
bbox = draw.textbbox((0, 0), title, font=font_title)
draw.text((right_x, 290), title, font=font_title, fill='#FFFFFF')

# 艺术家
artist = "Car Seat Headrest"
draw.text((right_x, 380), artist, font=font_artist, fill='#CCCCCC')

# 元信息：发行年份 | 收听次数
meta_y = 450
draw.text((right_x, meta_y), "发行年份", font=font_meta, fill='#666666')
draw.text((right_x, meta_y + 30), "2018", font=font_mv, fill='#DDDDDD')
draw.text((right_x + 280, meta_y), "收听次数", font=font_meta, fill='#666666')
draw.text((right_x + 280, meta_y + 30), "13 次", font=font_mv, fill='#DDDDDD')

# 风格标签
tags = ["Slacker Rock", "Rock"]
tag_y = meta_y + 100
for tag in tags:
    bbox = draw.textbbox((0, 0), tag, font=font_tag)
    tw = bbox[2] - bbox[0] + 40
    # 画标签背景
    draw.rounded_rectangle(
        [right_x, tag_y, right_x + tw, tag_y + 48],
        radius=24,
        fill=(255, 255, 255, 20)
    )
    draw.text((right_x + 20, tag_y + 8), tag, font=font_tag, fill='#BBBBBB')
    right_x += tw + 16

# 保存
bg.save(output_path, 'PNG')
print(f"Saved: {output_path}")
