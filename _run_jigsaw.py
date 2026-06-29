"""
_run_jigsaw.py — V项目 方案D重制：真正拼图效果
封面切成锯齿边缘，紧密排列
"""
import os, random, math
from PIL import Image, ImageDraw, ImageFilter, ImagePath
import numpy as np

W, H = 1920, 1080
random.seed(7)

PIECE_W = 380
PIECE_H = 270
COLS, ROWS = 5, 4
TAB = 28  # 拼图凸起大小


def make_jigsaw_mask(w, h, tab_w, tab_h, side_left, side_top, side_right, side_bottom):
    """生成一个拼图块的遮罩（白底黑形状）"""
    mask = Image.new('L', (w, h), 0)
    draw = ImageDraw.Draw(mask)

    # 四边中心点
    mid_top = w // 2
    mid_bot = w // 2
    mid_left = h // 2
    mid_right = h // 2

    pts = []

    # 左上角开始，顺时针
    pts = [(0, 0)]

    # 上边
    if side_top:
        # 向外凸起
        cx = mid_top - tab_w // 2
        pts += [
            (cx - tab_w // 2, 0),
            (cx - tab_w // 4, -tab_h),
            (cx + tab_w // 4, -tab_h),
            (cx + tab_w // 2, 0),
        ]
    pts += [(w, 0)]

    # 右边
    if side_right:
        cx = mid_right + tab_h // 2
        pts += [
            (w, cx - tab_h // 2),
            (w + tab_w, cx - tab_h // 4),
            (w + tab_w, cx + tab_h // 4),
            (w, cx + tab_h // 2),
        ]
    pts += [(w, h)]

    # 下边（反向）
    if side_bottom:
        cx = mid_bot + tab_w // 2
        pts += [
            (cx + tab_w // 2, h),
            (cx + tab_w // 4, h + tab_h),
            (cx - tab_w // 4, h + tab_h),
            (cx - tab_w // 2, h),
        ]
    pts += [(0, h)]

    # 左边（反向）
    if side_left:
        cx = mid_left - tab_h // 2
        pts += [
            (0, cx + tab_h // 2),
            (-tab_w, cx + tab_h // 4),
            (-tab_w, cx - tab_h // 4),
            (0, cx - tab_h // 2),
        ]
    pts += [(0, 0)]

    # 画多边形
    flat = []
    for px, py in pts:
        flat += [px, py]
    draw.polygon(flat, fill=255)
    return mask


def make_bg(covers):
    bg = covers[0].copy()
    bg = bg.filter(ImageFilter.GaussianBlur(18))
    bg = bg.resize((W, H), Image.LANCZOS)
    y_arr, x_arr = np.ogrid[:H, :W]
    cx, cy = W / 2, H / 2
    r = min(W, H) * 0.7
    d = np.sqrt((x_arr - cx)**2 + (y_arr - cy)**2) / r
    d = np.clip(d, 0, 1)
    vig = (1 - 0.65 * (1 - d)) * 255
    bg.paste(Image.fromarray(vig.astype(np.uint8), 'L'), (0, 0), Image.fromarray(vig.astype(np.uint8), 'L'))
    return bg


def resize_to_fit(cover, max_w, max_h):
    r = min(max_w / cover.width, max_h / cover.height)
    return cover.resize((int(cover.width * r), int(cover.height * r)), Image.LANCZOS)


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

    # 紧密拼图布局：每块紧凑排列，留1px间隔
    cell_w = W // COLS
    cell_h = H // ROWS

    placed = 0
    for row in range(ROWS):
        for col in range(COLS):
            idx = row * COLS + col
            if idx >= len(covers):
                break

            cover = covers[idx]

            # 缩放到略大于格子（让拼图边缘能被裁出）
            scale = 1.12
            tw = int(cell_w * scale)
            th = int(cell_h * scale)
            tile = resize_to_fit(cover, tw, th)

            # 计算拼图边的类型
            # 右凸/下凸，取决于行列位置（简单交替）
            side_right = (col < COLS - 1)  # 最右列无边
            side_bottom = (row < ROWS - 1)
            side_left = False
            side_top = False

            # 生成拼图遮罩
            mask = make_jigsaw_mask(
                tile.width, tile.height, TAB, TAB,
                side_left, side_top, side_right, side_bottom
            )

            # 模糊遮罩边缘（软化锯齿）
            mask_blur = mask.filter(ImageFilter.GaussianBlur(2))

            tile_a = tile.convert('RGBA')
            tile_a.putalpha(mask_blur)

            # 简化阴影
            shd = Image.new('RGBA', (tile.width, tile.height), (0, 0, 0, 0))
            sdraw = ImageDraw.Draw(shd)
            for i in range(1, 7):
                sdraw.rectangle([i, i, tile.width-1+i, tile.height-1+i],
                               fill=(0, 0, 0, 55 - i * 8))
            shd = shd.filter(ImageFilter.GaussianBlur(4))

            # 定位：tile居中于格子
            ox = col * cell_w + (cell_w - tile.width) // 2
            oy = row * cell_h + (cell_h - tile.height) // 2

            # 阴影层
            canvas.paste(shd, (ox + 5, oy + 5), shd)
            # 拼图层
            canvas.paste(tile_a, (ox, oy), tile_a)

            placed += 1

    # 格子分割线（拼图缝隙）
    draw = ImageDraw.Draw(canvas)
    for col in range(1, COLS):
        x = col * cell_w
        draw.line([(x, 0), (x, H)], fill=(0, 0, 0, 180), width=3)
    for row in range(1, ROWS):
        y = row * cell_h
        draw.line([(0, y), (W, y)], fill=(0, 0, 0, 180), width=3)

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
output = r'C:\Users\qujt\.qclaw\workspace\jigsaw_test.png'
process(paths, output)
