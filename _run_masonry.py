"""
_run_masonry.py — V项目 方案B：瀑布流（Masonry）
20张封面错落排列，像贴满墙的感觉
"""
import os, random
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

W, H = 1920, 1080
random.seed(99)

def make_bg(covers):
    bg = covers[0].copy()
    bg = bg.filter(ImageFilter.GaussianBlur(20))
    bg = bg.resize((W, H), Image.LANCZOS)
    y_arr, x_arr = np.ogrid[:H, :W]
    cx, cy = W / 2, H / 2
    r = min(W, H) * 0.72
    d = np.sqrt((x_arr - cx)**2 + (y_arr - cy)**2) / r
    d = np.clip(d, 0, 1)
    vig = (1 - 0.6 * (1 - d)) * 255
    bg.paste(Image.fromarray(vig.astype(np.uint8), 'L'), (0, 0), Image.fromarray(vig.astype(np.uint8), 'L'))
    return bg

def add_shadow(img, off=8):
    sw, sh = img.size
    shd = Image.new('RGBA', (sw+off*2, sh+off*2), (0,0,0,0))
    d = ImageDraw.Draw(shd)
    for s in range(off, 0, -1):
        d.rectangle([s, s, s+sw-1, s+sh-1], fill=(0,0,0,int(60-s*7)))
    shd = shd.filter(ImageFilter.GaussianBlur(6))
    out = Image.new('RGBA', shd.size, (0,0,0,0))
    out.paste(shd, (0,0))
    out.paste(img, (off, off))
    return out

def resize_tile(cover, max_w, max_h):
    ratio = min(max_w / cover.width, max_h / cover.height)
    nw = int(cover.width * ratio)
    nh = int(cover.height * ratio)
    return cover.resize((nw, nh), Image.LANCZOS)

def process(paths, output):
    covers = []
    for p in paths:
        try:
            covers.append(Image.open(p).convert('RGB'))
        except Exception as e:
            print(f'[SKIP] {os.path.basename(p)}: {e}')
    print(f'加载 {len(covers)} 张')
    if len(covers) < 4:
        return False

    bg = make_bg(covers)
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    canvas.paste(bg, (0, 0))

    # 瀑布流布局参数
    # 5列，列宽 340，每列之间间距 20
    cols = 5
    col_w = (W - 80) // cols
    col_gap = 20
    margin = 30

    # 每列起始高度 + 当前累计高度
    col_heights = [margin] * cols

    # 预计算每张封面缩放到列宽后的高度
    placed = []
    for i, cover in enumerate(covers):
        cw, ch = cover.size
        # 随机选一列偏移
        col = i % cols
        # 缩放
        scaled = resize_tile(cover, col_w - 16, 600)
        sw, sh = scaled.size
        # 找最矮的列
        min_col = min(range(cols), key=lambda c: col_heights[c])
        x = margin + min_col * (col_w + col_gap) + (col_w - sw) // 2
        y = col_heights[min_col]
        angle = random.uniform(-5, 5)
        if abs(angle) > 0.5:
            scaled = scaled.rotate(angle, expand=1, fillcolor=(30,30,35))
            sw, sh = scaled.size
        placed.append((scaled, x, y, sw, sh))
        col_heights[min_col] += sh + 18  # 块间距

    # 整体向下平移，让内容居中
    min_y = min(y for _, _, y, _, _ in placed)
    max_y = max(y + h for _, _, y, _, h in placed)
    total_h = max_y - min_y
    shift = max(0, (H - total_h) // 2 - min_y)

    for tile, x, y, sw, sh in placed:
        tile_a = tile.convert('RGBA')
        tile_s = add_shadow(tile_a, off=8)
        canvas.paste(tile_s, (x + 8, y + shift + 8), tile_s)
        canvas.paste(tile_a, (x, y + shift), tile_a)

    # 整体边框
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([15, 15, W-16, H-16], outline=(255,255,255,20), width=2)

    canvas.convert('RGB').save(output, 'PNG')
    print(f'[OK] -> {output}')
    return True

paths = [
    r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\1-李志-这个世界会好吗.jpg',
    r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\1-海龟先生-海龟先生-caa.jpg',
    r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\1-海龟先生-海龟先生.jpg',
    r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\10-林忆莲-盖亚.jpg',
    r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\100-黄舒骏-未来的街头.jpg',
    r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\101-周传雄-蓝色土耳其.jpg',
    r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\102-Supertramp-Famous Last Words.jpg',
    r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\103-ABBA-The Visitors.jpg',
    r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\104-Rita Calypso-Sicalyptico.jpg',
    r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\105-The Beatles-Please Please Me.jpg',
    r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\106-深山-雪山白凤凰.jpg',
    r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\107-Arcade Fire-Funeral.jpg',
    r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\108-王梵瑞-马秋峰.jpg',
    r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\109-谢天笑-冷血动物.jpg',
    r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\11-哪吒-他在时间门外.jpg',
    r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\110-谢天笑-只有一个愿望.jpg',
    r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\111-郑钧-第三只眼.jpg',
    r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\112-Carpenters-Now & Then.jpg',
    r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\113-陈升-我的小清新.jpg',
    r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\114-Supertramp-Even In The Quietest Moments.jpg',
]
output = r'C:\Users\qujt\.qclaw\workspace\masonry_test.png'
process(paths, output)
