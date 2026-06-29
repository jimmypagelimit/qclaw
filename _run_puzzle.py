"""
_run_puzzle.py — 内联运行 _gen_puzzle_mosaic 的测试
"""
import os, sys, random, math, argparse
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import numpy as np

W, H = 1920, 1080
random.seed(42)

def make_v3_bg(covers_list):
    sample = covers_list[0]
    bg = sample.copy()
    bg = bg.filter(ImageFilter.GaussianBlur(25))
    bg = bg.resize((W, H), Image.LANCZOS)
    y_arr, x_arr = np.ogrid[:H, :W]
    cx, cy = W / 2, H / 2
    r = min(W, H) * 0.72
    d = np.sqrt((x_arr - cx)**2 + (y_arr - cy)**2) / r
    d = np.clip(d, 0, 1)
    vig = (1 - 0.55 * (1 - d)) * 255
    vig_img = Image.fromarray(vig.astype(np.uint8), 'L')
    bg.paste(vig_img, (0, 0), vig_img)
    return bg.convert('RGBA')


def add_shadow(img, offset=6):
    sw, sh = img.size
    shadow = Image.new('RGBA', (sw + offset * 2, sh + offset * 2), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    for s in range(offset, 0, -1):
        alpha = int(55 - s * 7)
        sdraw.rectangle([s, s, s + sw - 1, s + sh - 1], fill=(0, 0, 0, alpha))
    shadow = shadow.filter(ImageFilter.GaussianBlur(5))
    result = Image.new('RGBA', shadow.size, (0, 0, 0, 0))
    result.paste(shadow, (0, 0))
    result.paste(img, (offset, offset))
    return result


def process(cover_paths, output_path):
    covers = []
    for p in cover_paths:
        try:
            img = Image.open(p).convert('RGB')
            covers.append(img)
        except Exception as e:
            print(f'[SKIP] {os.path.basename(p)}: {e}')
    print(f'加载 {len(covers)} 张封面')
    if len(covers) < 4:
        print('[ERROR] 至少需要 4 张')
        return False

    bg = make_v3_bg(covers)
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    canvas.paste(bg, (0, 0))

    grid_cols, grid_rows = 5, 4
    grid_w = W // grid_cols
    grid_h = H // grid_rows

    placed = 0
    for row in range(grid_rows):
        for col in range(grid_cols):
            idx = row * grid_cols + col
            if idx >= len(covers):
                break
            cover = covers[idx]
            # 缩放封面到格子
            cell_size = min(grid_w, grid_h) - 16
            sz = min(cover.size)
            left = (cover.width - sz) // 2
            top = (cover.height - sz) // 2
            tile = cover.crop((left, top, left + sz, top + sz))
            tile = tile.resize((cell_size, cell_size), Image.LANCZOS)

            # 随机旋转
            angle = random.uniform(-8, 8)
            if abs(angle) > 0.5:
                tile = tile.rotate(angle, expand=1, fillcolor=(30, 30, 35))

            # 加阴影
            tile_a = tile.convert('RGBA')
            tile_s = add_shadow(tile_a, offset=7)

            # 粘贴
            px = col * grid_w + (grid_w - cell_size) // 2
            py = row * grid_h + (grid_h - cell_size) // 2
            canvas.paste(tile_s, (px + 7, py + 7), tile_s)
            canvas.paste(tile_a, (px, py), tile_a)

            # 叠加碎片：从另一张封面取一块叠加
            other_idx = (idx + random.randint(1, len(covers) - 1)) % len(covers)
            other = covers[other_idx]
            frag_sz = cell_size // 2
            fx = random.randint(0, other.width - frag_sz)
            fy = random.randint(0, other.height - frag_sz)
            frag = other.crop((fx, fy, fx + frag_sz, fy + frag_sz))
            frag = frag.resize((frag_sz, frag_sz), Image.LANCZOS)
            fangle = random.uniform(-15, 15)
            frag = frag.rotate(fangle, expand=1, fillcolor=(30, 30, 35))
            frag_a = Image.new('RGBA', frag.size, (0, 0, 0, 0))
            frag_a.paste(frag, (0, 0))
            frag_a = frag_a.filter(ImageFilter.GaussianBlur(1))
            ox = px + random.randint(-cell_size // 3, cell_size // 3)
            oy = py + random.randint(-cell_size // 3, cell_size // 3)
            # 半透明叠加
            canvas_blend = canvas.copy()
            canvas.paste(frag_a, (ox, oy), frag_a)
            canvas = Image.blend(canvas_blend, canvas, 0.65)

            placed += 1

    # 格子点线边框
    draw = ImageDraw.Draw(canvas)
    for row in range(1, grid_rows):
        y = row * grid_h
        for x in range(0, W, 10):
            draw.ellipse([x, y, x + 3, y + 3], fill=(255, 255, 255, 35))
    for col in range(1, grid_cols):
        x = col * grid_w
        for y in range(0, H, 10):
            draw.ellipse([x, y, x + 3, y + 3], fill=(255, 255, 255, 35))

    canvas_rgb = canvas.convert('RGB')
    canvas_rgb.save(output_path, 'PNG')
    print(f'[OK] -> {output_path}')
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
output = r'C:\Users\qujt\.qclaw\workspace\puzzle_mosaic_test.png'
process(paths, output)
