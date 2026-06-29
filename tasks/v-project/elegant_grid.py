"""
elegant_grid.py — V项目精致网格布局

用法：
    python elegant_grid.py --test                   # 数据库前N张测试
    python elegant_grid.py --input 封面目录 --output out.png
    python elegant_grid.py --covers 封面1.jpg ... --output out.png
    python elegant_grid.py --albums 1,2,3           # 从数据库取指定专辑
    python elegant_grid.py --cols 6 --rows 6        # 6x6网格

设计：深色背景 + 正方形网格（循环填满，无空隙）
"""

import os, sys, random, argparse, importlib.util
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

W, H = 1920, 1080
MARGIN = 0
GAP = 0
RANDOM_SEED = 42


# ─── 背景 ───────────────────────────────────────────────

def make_bg(covers):
    """深色主调背景 + 微弱噪点纹理"""
    sample = covers[0]
    arr = np.array(sample.resize((10, 10)), dtype=float)
    avg = arr.mean(axis=(0, 1))
    r, g, b = int(avg[0]), int(avg[1]), int(avg[2])
    r, g, b = max(5, r//4), max(5, g//4), max(5, b//4)
    bg = Image.new('RGB', (W, H), (r, g, b))
    noise = Image.fromarray(
        (np.random.rand(H, W) * 12).astype(np.uint8), 'L'
    )
    bg.paste(noise, (0, 0), noise)
    return bg


def bg_color_from_bg(bg):
    """从背景图提取左上像素作为填充色"""
    arr = np.array(bg)
    return tuple(int(c) for c in arr[0, 0])


# ─── 封面处理 ────────────────────────────────────────────

def resize_fit(cover, tile_w, tile_h, crop_fill=True):
    """
    crop_fill=True : 裁切填充（填满四边，不变形）
    crop_fill=False: 等比放入（完整不变形，留白）
    """
    cover_ratio = cover.width / cover.height
    tile_ratio = tile_w / tile_h
    if crop_fill:
        if cover_ratio > tile_ratio:
            new_w = int(cover.height * tile_ratio)
            left = (cover.width - new_w) // 2
            cover = cover.crop((left, 0, left + new_w, cover.height))
        else:
            new_h = int(cover.width / tile_ratio)
            top = (cover.height - new_h) // 2
            cover = cover.crop((0, top, cover.width, top + new_h))
    else:
        r = min(tile_w / cover.width, tile_h / cover.height)
        w, h = int(cover.width * r), int(cover.height * r)
        cover = cover.resize((w, h), Image.LANCZOS)
    return cover.resize((tile_w, tile_h), Image.LANCZOS)


def paste_card(canvas, cover, x, y, tile_w, tile_h):
    """封面裁切填满正方形格子，居中"""
    tile = resize_fit(cover, tile_w, tile_h, crop_fill=True)
    canvas.paste(tile, (x, y))


# ─── 花朵装饰 ────────────────────────────────────────────

def _petal(canvas, cx, cy, angle, size, color):
    """画一个花瓣（椭圆）"""
    rad = np.radians(angle)
    px = int(np.cos(rad) * size * 1.8)
    py = int(np.sin(rad) * size * 1.8)
    draw = ImageDraw.Draw(canvas, 'RGBA')
    draw.ellipse([cx + px - size, cy + py - size//2,
                  cx + px + size, cy + py + size//2],
                 fill=color)


def add_flower(canvas, cx, cy, color, size=7):
    """在(cx, cy)画一朵小花：四瓣 + 花蕊"""
    r, g, b = color
    alpha = 230
    color_a = (r, g, b, alpha)
    for angle in [0, 90, 180, 270]:
        _petal(canvas, cx, cy, angle, size, color_a)
    draw = ImageDraw.Draw(canvas, 'RGBA')
    draw.ellipse([cx - size//2, cy - size//2,
                  cx + size//2, cy + size//2],
                 fill=(255, 255, 240, 255))


def add_corner_flower(canvas, color, cols, rows, tile_size, ox, oy):
    """四角格子中心各放一朵大花"""
    corners = [
        (ox + tile_size//2,         oy + tile_size//2),
        (ox + (cols-1)*tile_size + tile_size//2, oy + tile_size//2),
        (ox + tile_size//2,         oy + (rows-1)*tile_size + tile_size//2),
        (ox + (cols-1)*tile_size + tile_size//2, oy + (rows-1)*tile_size + tile_size//2),
    ]
    for fx, fy in corners:
        add_flower(canvas, fx, fy, color, size=9)


def add_border_flowers(canvas, color, cols, rows, tile_size, ox, oy):
    """四边均匀分布小花（每隔1.5格放一朵）"""
    rng = random.Random(77)
    step = int(tile_size * 1.5)
    fc = color

    # 上边 / 下边
    for x in range(ox, ox + cols * tile_size, step):
        for y_edge, sign in [(oy, 1), (oy + rows*tile_size, -1)]:
            offset = rng.randint(4, 10) * sign
            if rng.random() < 0.65:
                add_flower(canvas, x + rng.randint(-3,3), y_edge + offset,
                           fc, size=rng.randint(3, 6))
    # 左边 / 右边
    for y in range(oy, oy + rows * tile_size, step):
        for x_edge, sign in [(ox, 1), (ox + cols*tile_size, -1)]:
            offset = rng.randint(4, 10) * sign
            if rng.random() < 0.65:
                add_flower(canvas, x_edge + offset, y + rng.randint(-3,3),
                           fc, size=rng.randint(3, 6))


def add_grid_intersection_dots(canvas, color, cols, rows, tile_size, ox, oy):
    """网格交叉点放小圆点（约40%概率）"""
    rng = random.Random(33)
    r, g, b = color
    dot_a = (r, g, b, 180)

    # 横线交点
    for row in range(1, rows):
        y = oy + row * tile_size
        for col in range(cols + 1):
            x = ox + col * tile_size
            if rng.random() < 0.4:
                d = rng.randint(2, 5)
                draw = ImageDraw.Draw(canvas, 'RGBA')
                draw.ellipse([x-d, y-d, x+d, y+d], fill=dot_a)

    # 竖线交点
    for col in range(1, cols):
        x = ox + col * tile_size
        for row in range(rows + 1):
            y = oy + row * tile_size
            if rng.random() < 0.4:
                d = rng.randint(2, 5)
                draw = ImageDraw.Draw(canvas, 'RGBA')
                draw.ellipse([x-d, y-d, x+d, y+d], fill=dot_a)


def add_eyebrow_lines(canvas, color, cols, rows, tile_size, ox, oy):
    """每格顶部加一根细细的眉毛线（光泽感）"""
    draw = ImageDraw.Draw(canvas, 'RGBA')
    r, g, b = color
    lc = (min(255, r+60), min(255, g+60), min(255, b+60), 80)
    for row in range(rows):
        for col in range(cols):
            x = ox + col * tile_size
            y = oy + row * tile_size
            draw.line([(x+6, y+2), (x+tile_size-6, y+2)],
                      fill=lc, width=1)


# ─── 加载封面 ────────────────────────────────────────────

def load_from_dir(directory, limit=None):
    exts = ('.jpg', '.jpeg', '.png', '.webp')
    files = sorted([
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.lower().endswith(exts)
    ])
    covers = []
    for p in files:
        try:
            covers.append(Image.open(p).convert('RGB'))
        except:
            pass
        if limit and len(covers) >= limit:
            break
    return covers


def load_from_albums(db_path, limit=36):
    import sqlite3
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "SELECT album_id FROM albums "
        "WHERE cover_image_url IS NOT NULL "
        "ORDER BY album_id LIMIT ?", (limit,)
    )
    rows = [r[0] for r in cur.fetchall()]
    conn.close()

    covers_dir = os.path.join(
        os.path.dirname(db_path),
        'tasks', '2026-05-12-long-term-project',
        'album-tracker', 'public', 'covers'
    )
    covers = []
    for album_id in rows:
        prefix = f"{album_id}-"
        matched = [f for f in os.listdir(covers_dir)
                   if f.startswith(prefix) and f.endswith('.jpg')]
        if matched:
            try:
                covers.append(
                    Image.open(os.path.join(covers_dir, matched[0])).convert('RGB')
                )
            except:
                pass
    return covers


# ─── 主函数 ──────────────────────────────────────────────

def run(input_dir=None, output='elegant_grid.png',
        covers=None, db_path=None, limit=36,
        cols=6, rows=6, seed=RANDOM_SEED):
    random.seed(seed)

    if covers:
        pass
    elif input_dir:
        covers = load_from_dir(input_dir, limit)
    elif db_path:
        covers = load_from_albums(db_path, limit)
    else:
        print('[ERROR] 需要提供封面目录、文件列表或数据库路径')
        sys.exit(1)

    if len(covers) == 0:
        print('[ERROR] 未加载到任何封面')
        sys.exit(1)

    # 背景
    bg = make_bg(covers[:min(5, len(covers))])
    canvas = bg
    bc = bg_color_from_bg(bg)  # 背景色

    # 正方形格子
    tile_size = H // rows          # 180
    total_w  = cols * tile_size   # 1080
    ox = (W - total_w) // 2       # 横向居中
    oy = 0

    # 填满网格（循环）
    n = len(covers)
    placed = 0
    for row in range(rows):
        for col in range(cols):
            idx = placed % n
            x = ox + col * tile_size
            y = oy + row * tile_size
            paste_card(canvas, covers[idx], x, y, tile_size, tile_size)
            placed += 1

    # ── 花朵装饰 ──
    r, g, b = bc
    flower_color = (
        min(255, r * 2 + 30),
        min(255, g * 2 + 30),
        min(255, b * 2 + 30),
    )

    # 1. 四角大花
    add_corner_flower(canvas, flower_color, cols, rows, tile_size, ox, oy)

    # 2. 网格交叉点小圆点
    add_grid_intersection_dots(canvas, flower_color, cols, rows, tile_size, ox, oy)

    # 3. 四边小花
    add_border_flowers(canvas, flower_color, cols, rows, tile_size, ox, oy)

    # 4. 眉线光泽
    add_eyebrow_lines(canvas, flower_color, cols, rows, tile_size, ox, oy)

    canvas.save(output, 'PNG')
    print(f'[OK] {output}')
    return output


# ─── CLI ────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', '-i', default=None)
    ap.add_argument('--output', '-o', default='elegant_grid.png')
    ap.add_argument('--covers', nargs='+', default=None)
    ap.add_argument('--db', default=None)
    ap.add_argument('--limit', '-n', type=int, default=36)
    ap.add_argument('--cols', type=int, default=6)
    ap.add_argument('--rows', type=int, default=6)
    ap.add_argument('--seed', type=int, default=RANDOM_SEED)
    ap.add_argument('--test', action='store_true')
    args = ap.parse_args()

    covers, input_dir, db_path = None, None, None

    if args.test:
        db_path = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
    elif args.input:
        input_dir = args.input
    elif args.covers:
        covers = []
        for p in args.covers:
            try:
                covers.append(Image.open(p).convert('RGB'))
            except Exception as e:
                print(f'[SKIP] {p}: {e}')
    elif args.db:
        db_path = args.db
    else:
        db_path = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'

    run(input_dir=input_dir, covers=covers, db_path=db_path,
        output=args.output, limit=args.limit,
        cols=args.cols, rows=args.rows, seed=args.seed)


if __name__ == '__main__':
    main()
