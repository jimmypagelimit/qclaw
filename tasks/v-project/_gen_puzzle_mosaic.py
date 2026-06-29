"""
_gen_puzzle_mosaic.py — V项目 方案D：封面碎片拼贴

20张专辑封面 → 切成碎片 → 散落组合成一张图

设计：
- 每个封面切成 3 块不规则碎片
- 碎片带随机旋转（-15°~+15°）
- 碎片有投影（立体感）
- 背景用 V3 底子（模糊+暗角）
- 碎片边缘有轻微描边（拼图感）

用法:
    python _gen_puzzle_mosaic.py --input DIR --output OUT.png
    python _gen_puzzle_mosaic.py --test 封面1.jpg 封面2.jpg ... 封面20.jpg
"""

import os, sys, random, math, argparse
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import numpy as np


W, H = 1920, 1080
random.seed(42)


def cut_into_fragments(cover, n=3):
    """把封面切成 n 块不规则碎片，返回碎片列表 [(img, x, y, angle)]"""
    cw, ch = cover.size
    fragments = []
    fw = cw // n
    for i in range(n):
        # 每块宽度略有不同
        w = fw + random.randint(-fw//6, fw//6)
        x = i * fw + random.randint(-fw//8, fw//8)
        x = max(0, min(cw - w, x))
        # 高度也略有裁切，模拟不规则碎片
        y_off = random.randint(-ch//10, ch//10)
        y = max(0, y_off)
        h = ch - abs(y_off)
        frag = cover.crop((x, y, x + w, y + h))
        # 缩放回原封面尺寸，保持一致
        frag = frag.resize((cw, ch), Image.LANCZOS)
        angle = random.uniform(-12, 12)
        fragments.append((frag, x, y, angle))
    return fragments


def place_fragment(canvas, frag_img, base_x, base_y, angle, shadow=True):
    """把碎片粘贴到画布上（带投影）"""
    cw, ch = frag_img.size
    # 旋转
    if abs(angle) > 0.5:
        frag_rot = frag_img.rotate(angle, expand=1, fillcolor=(30, 30, 35))
    else:
        frag_rot = frag_img
    rw, rh = frag_rot.size

    # 投影
    if shadow:
        shadow_img = Image.new('RGBA', (rw + 12, rh + 12), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_img)
        # 投影偏移
        for s in range(8, 0, -1):
            alpha = int(60 - s * 7)
            ox, oy = s, s
            shadow_draw.rectangle([ox, oy, ox + rw - 1, oy + rh - 1],
                                  fill=(0, 0, 0, alpha))
        shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(6))

        # 合成投影
        result = Image.new('RGBA', (rw + 12, rh + 12), (0, 0, 0, 0))
        result.paste(shadow_img, (0, 0))
        result.paste(frag_rot, (6, 6))
    else:
        result = frag_rot

    # 粘贴到画布
    cx = base_x - rw // 2
    cy = base_y - rh // 2
    canvas.paste(result, (cx, cy), result)
    return cx, cy, rw, rh


def make_v3_bg(covers_list, sample_cover):
    """生成 V3 风格背景：模糊封面 + 暗角"""
    bg = sample_cover.copy()
    bg = bg.filter(ImageFilter.GaussianBlur(25))
    bg = bg.resize((W, H), Image.LANCZOS)

    # 暗角
    y_arr, x_arr = np.ogrid[:H, :W]
    cx, cy = W / 2, H / 2
    r = min(W, H) * 0.72
    d = np.sqrt((x_arr - cx)**2 + (y_arr - cy)**2) / r
    d = np.clip(d, 0, 1)
    vig = (1 - 0.55 * (1 - d)) * 255
    vig_img = Image.fromarray(vig.astype(np.uint8), 'L')
    bg.paste(vig_img, (0, 0), vig_img)

    return bg.convert('RGBA')


def make_puzzle_grid(fragments_list, canvas_w, canvas_h, n_cols=5, n_rows=4):
    """把碎片网格排列，有轻微随机偏移"""
    positions = []
    cell_w = canvas_w // n_cols
    cell_h = canvas_h // n_rows
    margin = 20

    for row in range(n_rows):
        for col in range(n_cols):
            x = col * cell_w + cell_w // 2 + random.randint(-margin, margin)
            y = row * cell_h + cell_h // 2 + random.randint(-margin, margin)
            positions.append((x, y))

    random.shuffle(positions)

    placed = []
    for i, (frag_img, _, _, angle) in enumerate(fragments_list):
        if i < len(positions):
            px, py = positions[i]
            placed.append((frag_img, px, py, angle))
        else:
            # 太多碎片，放不下
            placed.append((frag_img,
                           random.randint(100, canvas_w - 100),
                           random.randint(100, canvas_h - 100),
                           angle))
    return placed


def process(cover_paths, output_path):
    """主函数"""
    # 1. 加载所有封面
    covers = []
    for p in cover_paths:
        try:
            img = Image.open(p).convert('RGB')
            covers.append(img)
        except Exception as e:
            print(f'  [SKIP] {os.path.basename(p)}: {e}')
    print(f'加载 {len(covers)} 张封面')

    if len(covers) < 4:
        print('[ERROR] 至少需要 4 张封面')
        return False

    # 2. 每张封面切成碎片
    all_fragments = []
    for i, cover in enumerate(covers):
        frags = cut_into_fragments(cover, n=3)
        all_fragments.extend(frags)
    random.shuffle(all_fragments)
    print(f'共 {len(all_fragments)} 个碎片')

    # 3. 生成背景
    bg = make_v3_bg(covers, covers[0])
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    canvas.paste(bg, (0, 0))

    # 4. 排列碎片到网格
    # 5列×4行=20格，刚好放20个封面的主碎片
    # 每个主碎片位置用其第一块
    main_fragments = [(covers[i], i * 0) for i in range(len(covers))]
    # 直接用封面切片排列
    cover_positions = make_puzzle_grid(
        [(c, 0, 0, 0) for c in covers], W, H, n_cols=5, n_rows=4
    )

    # 5. 放置每个封面（缩放到合适大小）到对应格子
    grid_w = W // 5
    grid_h = H // 4
    placed_covers = 0

    for row in range(4):
        for col in range(5):
            idx = row * 5 + col
            if idx >= len(covers):
                break
            cover = covers[idx]
            # 缩放封面到格子大小（留边距）
            target_size = min(grid_w, grid_h) - 16
            scaled = cover.copy()
            sz = min(scaled.size)
            left = (scaled.width - sz) // 2
            top = (scaled.height - sz) // 2
            scaled = scaled.crop((left, top, left + sz, top + sz))
            scaled = scaled.resize((target_size, target_size), Image.LANCZOS)

            # 随机旋转（-8°~+8°）
            angle = random.uniform(-8, 8)
            if abs(angle) > 1:
                scaled = scaled.rotate(angle, expand=1, fillcolor=(30, 30, 35))

            # 投影
            sw, sh = scaled.size
            shadow = Image.new('RGBA', (sw + 10, sh + 10), (0, 0, 0, 0))
            sdraw = ImageDraw.Draw(shadow)
            for s in range(7, 0, -1):
                alpha = int(50 - s * 6)
                sdraw.rectangle([s, s, s + sw - 1, s + sh - 1],
                                fill=(0, 0, 0, alpha))
            shadow = shadow.filter(ImageFilter.GaussianBlur(5))

            # 拼贴到底板
            paste_x = col * grid_w + (grid_w - target_size) // 2
            paste_y = row * grid_h + (grid_h - target_size) // 2

            # 投影层
            canvas.paste(shadow, (paste_x + 5, paste_y + 5), shadow)
            # 封面层
            canvas.paste(scaled, (paste_x, paste_y), scaled)

            # 碎片拼图效果：在封面上面再加一块小碎片
            # 随机选另一张封面的一个碎片叠加
            other_idx = (idx + random.randint(1, len(covers) - 1)) % len(covers)
            other_cover = covers[other_idx]
            frag_sz = target_size // 2
            frag_x = random.randint(0, target_size - frag_sz)
            frag_y = random.randint(0, target_size - frag_sz)
            frag = other_cover.crop((
                other_cover.width // 4 + frag_x,
                other_cover.height // 4 + frag_y,
                other_cover.width // 4 + frag_x + frag_sz,
                other_cover.height // 4 + frag_y + frag_sz
            ))
            sz2 = min(frag.size)
            frag = frag.crop((0, 0, sz2, sz2))
            frag = frag.resize((frag_sz, frag_sz), Image.LANCZOS)
            frag_a = Image.new('RGBA', (frag_sz, frag_sz), (255, 255, 255, 0))

            # 旋转碎片
            fangle = random.uniform(-15, 15)
            frag_rot = frag.rotate(fangle, expand=1, fillcolor=(30, 30, 35))
            frag_ra = Image.new('RGBA', frag_rot.size, (255, 255, 255, 0))
            frag_ra.paste(frag_rot, (0, 0))
            frag_ra = frag_ra.filter(ImageFilter.GaussianBlur(1))

            # 叠加碎片（60%透明度）
            ox = paste_x + random.randint(-target_size // 4, target_size // 4)
            oy = paste_y + random.randint(-target_size // 4, target_size // 4)

            overlay = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
            overlay.paste(frag_ra, (ox, oy), frag_ra)
            # 用 mask 混合
            canvas = Image.alpha_composite(canvas, overlay)

            placed_covers += 1

    # 6. 整体加一层细边框（拼图感）
    draw = ImageDraw.Draw(canvas)
    # 画内部格子线（虚线效果，点线）
    for row in range(1, 4):
        y = row * grid_h
        for x in range(0, W, 8):
            draw.ellipse([x, y, x + 2, y + 2], fill=(255, 255, 255, 30))
    for col in range(1, 5):
        x = col * grid_w
        for y in range(0, H, 8):
            draw.ellipse([x, y, x + 2, y + 2], fill=(255, 255, 255, 30))

    # 7. 转为 RGB 保存
    canvas_rgb = canvas.convert('RGB')
    canvas_rgb.save(output_path, 'PNG')
    print(f'[OK]  → {output_path}')
    return True


def main():
    parser = argparse.ArgumentParser(description='V项目 方案D：封面碎片拼贴')
    parser.add_argument('--input', default=None, help='封面目录')
    parser.add_argument('--output', default=None, help='输出文件路径')
    parser.add_argument('--test', nargs='+', help='测试多张封面路径')
    args = parser.parse_args()

    if args.test:
        paths = args.test
        output = args.test[0].replace('.jpg', '_puzzle.png').replace('.jpeg', '_puzzle.png')
    elif args.input:
        exts = ('.jpg', '.jpeg', '.png', '.webp')
        paths = sorted([
            os.path.join(args.input, f)
            for f in os.listdir(args.input)
            if f.lower().endswith(exts)
        ])
        output = args.output or 'puzzle_mosaic.png'
    else:
        print('[ERROR] 需要 --input DIR 或 --test 封面1.jpg ...')
        sys.exit(1)

    print(f'处理 {len(paths)} 张封面 → {output}')
    ok = process(paths, output)
    if not ok:
        sys.exit(1)


if __name__ == '__main__':
    main()
