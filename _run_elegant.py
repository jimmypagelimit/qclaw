"""
_run_elegant.py — V项目精致版
杂志排版感：干净、留白、有呼吸感
"""
import os, random
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

W, H = 1920, 1080
random.seed(42)

BG_COLOR = (10, 10, 12)  # 深色底子
CARD_GAP = 10
MARGIN = 50

def make_bg(covers):
    """从封面提取主色作为背景"""
    sample = covers[0]
    # 缩小采样
    arr = np.array(sample.resize((20, 20)), dtype=float)
    avg = arr.mean(axis=(0,1))
    r, g, b = int(avg[0]), int(avg[1]), int(avg[2])
    # 压暗
    r, g, b = max(5, r//5), max(5, g//5), max(5, b//5)
    bg = Image.new('RGB', (W, H), (r, g, b))
    # 模糊叠加纹理
    noise = Image.fromarray(
        (np.random.rand(H, W) * 15).astype(np.uint8), 'L'
    )
    bg.paste(noise, (0, 0), noise)
    return bg

def add_shadow(size, off=12):
    """圆角矩形阴影"""
    w, h = size
    shd_w = w + off * 2
    shd_h = h + off * 2
    shd = Image.new('RGBA', (shd_w, shd_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(shd)
    # 多次叠加模拟软阴影
    for i in range(off, 0, -1):
        alpha = 50 - i * 3
        draw.rounded_rectangle(
            [i, i, shd_w-1-i, shd_h-1-i],
            radius=max(4, 10 - i),
            fill=(0, 0, 0, alpha)
        )
    shd = shd.filter(ImageFilter.GaussianBlur(8))
    return shd

def resize_with_aspect(cover, max_w, max_h):
    r = min(max_w / cover.width, max_h / cover.height)
    return cover.resize((int(cover.width*r), int(cover.height*r)), Image.LANCZOS)

def paste_card(canvas, cover, x, y, card_w, card_h):
    """把封面居中放入卡片区域，加阴影再粘贴"""
    tile = resize_with_aspect(cover, card_w - 6, card_h - 6)
    tw, th = tile.size

    # 阴影
    shadow = add_shadow((tw, th), off=12)
    ox = x + (card_w - tw) // 2
    oy = y + (card_h - th) // 2
    canvas.paste(shadow, (ox - 12, oy - 12), shadow)

    # 圆角边框
    border = Image.new('RGBA', (tw+2, th+2), (255,255,255,12))
    bdraw = ImageDraw.Draw(border)
    bdraw.rounded_rectangle([0,0,tw+1,th+1], radius=5, outline=(255,255,255,35), width=1)
    canvas.paste(border, (ox-1, oy-1), border)

    # 粘贴封面
    canvas.paste(tile, (ox, oy))

def process(paths, output):
    covers = []
    for p in paths:
        try:
            covers.append(Image.open(p).convert('RGB'))
        except Exception as e:
            print(f'[SKIP] {os.path.basename(p)}')
    print(f'加载 {len(covers)} 张')
    if len(covers) < 4:
        return False

    bg = make_bg(covers)
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    canvas.paste(bg, (0, 0))

    # 杂志布局：5列，2行大+1行小
    # 布局规则：封面竖向排列，横向分5格
    cols = 5
    available_w = W - MARGIN * 2
    card_w = (available_w - CARD_GAP * (cols - 1)) // cols
    available_h = H - MARGIN * 2
    # 20张: 前15张分5列3行(每行高=可用高/3)，后5张放底部一行
    row_h_large = available_h // 3
    row_h_small = available_h // 4

    placed = 0

    # 前15张：3行
    for row in range(3):
        for col in range(5):
            idx = row * 5 + col
            if idx >= len(covers):
                break
            cx = MARGIN + col * (card_w + CARD_GAP)
            cy = MARGIN + row * (row_h_large + CARD_GAP)
            paste_card(canvas, covers[idx], cx, cy, card_w, row_h_large)
            placed += 1

    # 后5张：底部一行，稍大
    small_card_w = (available_w - CARD_GAP * 4) // 5
    for col in range(5):
        idx = 15 + col
        if idx >= len(covers):
            break
        cx = MARGIN + col * (small_card_w + CARD_GAP)
        cy = H - MARGIN - row_h_small
        paste_card(canvas, covers[idx], cx, cy, small_card_w, row_h_small)
        placed += 1

    # 底部装饰线
    draw = ImageDraw.Draw(canvas)
    line_y = H - MARGIN - row_h_small - 20
    draw.rectangle([MARGIN, line_y, W - MARGIN, line_y + 1], fill=(255,255,255,25))
    draw.rectangle([MARGIN, line_y + 3, W - MARGIN, line_y + 4], fill=(255,255,255,15))

    # 顶角装饰
    draw.ellipse([MARGIN-3, MARGIN-3, MARGIN+3, MARGIN+3], fill=(255,255,255,30))
    draw.ellipse([W-MARGIN-3, MARGIN-3, W-MARGIN+3, MARGIN+3], fill=(255,255,255,30))

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
output = r'C:\Users\qujt\.qclaw\workspace\elegant_test.png'
process(paths, output)
