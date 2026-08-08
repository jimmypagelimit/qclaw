"""
_gen_batch_bg_v3.py — V4 精致版

V3底子（完全保留）：
- 椭圆暗角（平滑过渡）
- 右侧缓慢渐暗
- 封面左上角镜面高光
- CD装饰（深色边框+中心孔）
- 动态配色（封面边框从封面提取主色）
- 封面阴影（增加立体感）
- 轻微胶片颗粒（艺术化纹理）

V4新增：
- 去掉右上角圆点
- 随机模糊半径（35~50，每张不同）
- 随机色温偏移（冷暖倾向，每张不同）
- 随机暗角强度、颗粒强度、阴影强度
- 每张图独一无二的微妙质感

用法:
    python _gen_batch_bg_v3.py --test 封面路径
    python _gen_batch_bg_v3.py --input DIR
"""

import os, sys, math, random, argparse
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print('[WARN] NumPy未安装，使用慢速版')

try:
    import colorsys
    HAS_COLORSYS = True
except ImportError:
    HAS_COLORSYS = False

from PIL import Image, ImageDraw, ImageFilter


# ═══════════════════════════════════════════════════
# V2 原始参数（不动）
# ═══════════════════════════════════════════════════
W, H = 1920, 1080
COVER_X = 180
COVER_SIZE = 550
CD_BORDER = 16
CD_LINE_COLOR = (60, 50, 64)
CD_INNER_R = 55
CD_HOLE_R = 14
DOT_RADIUS = 6
DOT_GAP = 30
DOT_TOP = 30
VIGNETTE_STRENGTH = 0.65
# 渐暗：从封面右侧开始，缓慢延伸到画面边缘（无硬边界）
RIGHT_FADE_START = COVER_X + COVER_SIZE  # 封面右边缘开始
RIGHT_FADE_END = W - 100  # 一直延伸到靠近右边缘


# ═══════════════════════════════════════════════════
# 工具函数
# ═══════════════════════════════════════════════════

def hsv_to_rgb(h, s, v):
    """HSV → RGB"""
    if HAS_COLORSYS:
        r, g, b = colorsys.hsv_to_rgb(h/360, s, v)
        return int(r*255), int(g*255), int(b*255)
    c = v * s
    x = c * (1 - abs((h/60) % 2 - 1))
    m = v - c
    if h < 60:   r, g, b = c, x, 0
    elif h < 120: r, g, b = x, c, 0
    elif h < 180: r, g, b = 0, c, x
    elif h < 240: r, g, b = 0, x, c
    elif h < 300: r, g, b = x, 0, c
    else:         r, g, b = c, 0, x
    return int((r+m)*255), int((g+m)*255), int((b+m)*255)


def extract_dominant_color(cover_img):
    """从封面提取主色（用于动态配色）"""
    if not HAS_NUMPY:
        return (212, 175, 55)
    try:
        small = cover_img.copy().resize((50, 50), Image.LANCZOS)
        arr = np.array(small, dtype=np.float32)
        pixels = arr.reshape(-1, 3)
        k = 3
        idx = np.random.choice(len(pixels), k, replace=False)
        centers = pixels[idx].copy()
        for _ in range(5):
            dists = np.linalg.norm(pixels[:, None] - centers, axis=2)
            labels = np.argmin(dists, axis=1)
            for i in range(k):
                if np.any(labels == i):
                    centers[i] = pixels[labels == i].mean(axis=0)
        brightest = max(centers, key=lambda c: np.mean(c))
        return tuple(int(max(0, min(255, c))) for c in brightest)
    except:
        return (212, 175, 55)


def make_vignette(w, h, strength=VIGNETTE_STRENGTH):
    """椭圆形渐变暗角 — 自然过渡，无硬边界"""
    if HAS_NUMPY:
        y, x = np.ogrid[:h, :w]
        cx, cy = w / 2, h / 2
        # 椭圆半径：水平宽、垂直窄，让暗角更自然
        rx = w * 0.55
        ry = h * 0.65
        d = np.sqrt(((x - cx) / rx)**2 + ((y - cy) / ry)**2)
        d = np.clip(d, 0, 1)
        # 平滑曲线 (power curve) 让过渡更柔和
        d = d ** 1.5
        vignette = (1 - strength * d) * 255
        return Image.fromarray(vignette.astype(np.uint8), 'L')
    else:
        img = Image.new('L', (w, h), 255)
        draw = ImageDraw.Draw(img)
        cx, cy = w // 2, h // 2
        rx, ry = w * 0.55, h * 0.65
        for y in range(h):
            for x in range(w):
                d = math.sqrt(((x - cx) / rx)**2 + ((y - cy) / ry)**2)
                d = min(1.0, max(0.0, d))
                d = d ** 1.5
                v = int(255 * (1 - strength * d))
                draw.point((x, y), v)
        return img


def make_right_fade(w, h, fade_start, fade_end):
    """右侧渐暗 — 缓慢过渡，无硬边界"""
    fade = Image.new('L', (w, h), 0)
    if HAS_NUMPY:
        x = np.arange(w)
        # 使用平滑曲线: 0→1 在 fade_start 到 fade_end 之间
        alpha = np.clip((x - fade_start) / (fade_end - fade_start), 0, 1)
        # 平滑曲线，让暗部过渡更自然
        alpha = alpha ** 1.2
        alpha = alpha * 180  # 最大暗度降低，避免太黑
        fade_arr = np.tile(alpha, (h, 1)).astype(np.uint8)
        fade = Image.fromarray(fade_arr, 'L')
    else:
        draw = ImageDraw.Draw(fade)
        for x in range(w):
            t = min(1.0, max(0.0, (x - fade_start) / (fade_end - fade_start)))
            t = t ** 1.2
            v = int(t * 180)
            for y in range(h):
                fade.putpixel((x, y), v)
    return fade


def make_cover_gloss(cover_x, cover_y, cover_size):
    """封面左上角镜面高光（V2原版）"""
    gloss = Image.new('L', (W, H), 0)
    draw = ImageDraw.Draw(gloss)
    gloss_w = 60
    gloss_h = cover_size
    cx = cover_x + 20
    cy = cover_y + 10
    for i in range(gloss_w):
        alpha = int(40 * (1 - i / gloss_w))
        offset = int(i * 0.4)
        x1 = cx - gloss_w + i
        draw.line([x1, cy + offset, x1, cy + gloss_h], fill=alpha, width=1)
    return gloss.filter(ImageFilter.GaussianBlur(15))


# ═══════════════════════════════════════════════════
# 主处理流程
# ═══════════════════════════════════════════════════

def process_v3(cover_path, output_path):
    try:
        cover = Image.open(cover_path).convert('RGB')
    except Exception as e:
        print(f'  [SKIP] 无法打开: {e}')
        return False

    # 封面裁切
    cover_y = (H - COVER_SIZE) // 2
    sz = min(cover.size)
    left = (cover.width - sz) // 2
    top = (cover.height - sz) // 2
    cover_sq = cover.crop((left, top, left + sz, top + sz))
    cover_resized = cover_sq.resize((COVER_SIZE, COVER_SIZE), Image.LANCZOS)

    cd_cx = COVER_X + COVER_SIZE // 2
    cd_cy = cover_y + COVER_SIZE // 2
    cd_outer_r = COVER_SIZE // 2 + CD_BORDER

    # 动态配色：从封面提取主色
    dom_color = extract_dominant_color(cover)
    border_color = dom_color

    # 随机种子：每张图引入微小随机差异，体现设计用心
    rand_seed = hash(cover_path) % 10000
    random.seed(rand_seed)

    # 1. 模糊背景（随机半径 35~50，每张图不同）
    blur_r = random.randint(35, 50)
    bg = cover.copy().resize((W, H))
    bg = bg.filter(ImageFilter.GaussianBlur(blur_r))

    # 2. 随机轻微色温偏移（冷暖倾向）
    if HAS_NUMPY:
        warm_shift = random.uniform(-8, 8)  # -8冷 +8暖
        bg_arr = np.array(bg, dtype=np.float32)
        if warm_shift > 0:
            bg_arr[:, :, 0] = np.clip(bg_arr[:, :, 0] + warm_shift * 0.5, 0, 255)  # R+
            bg_arr[:, :, 2] = np.clip(bg_arr[:, :, 2] - warm_shift * 0.3, 0, 255)  # B-
        else:
            bg_arr[:, :, 0] = np.clip(bg_arr[:, :, 0] + warm_shift * 0.3, 0, 255)  # R-
            bg_arr[:, :, 2] = np.clip(bg_arr[:, :, 2] - warm_shift * 0.5, 0, 255)  # B+
        bg = Image.fromarray(bg_arr.astype(np.uint8), 'RGB')

    # 3. 暗角（随机强度轻微浮动）
    vig_strength = VIGNETTE_STRENGTH + random.uniform(-0.05, 0.05)
    vig = make_vignette(W, H, vig_strength)
    if HAS_NUMPY:
        bg_arr = np.array(bg, dtype=np.float32)
        vig_arr = np.array(vig, dtype=np.float32) / 255.0
        for c in range(3):
            bg_arr[:, :, c] *= vig_arr
        bg = Image.fromarray(np.clip(bg_arr, 0, 255).astype(np.uint8), 'RGB')
    else:
        for y in range(H):
            for x in range(W):
                v = vig.getpixel((x, y)) / 255.0
                r, g, b = bg.getpixel((x, y))
                bg.putpixel((x, y), (
                    int(r * v), int(g * v), int(b * v)
                ))

    # 3. 右侧渐暗 — 缓慢过渡，无硬边界
    rf = make_right_fade(W, H, RIGHT_FADE_START, RIGHT_FADE_END)
    rf_pixels = rf.load()
    if HAS_NUMPY:
        bg_arr = np.array(bg, dtype=np.float32)
        for y in range(H):
            for x in range(W):
                alpha = rf_pixels[x, y] / 255.0
                bg_arr[y, x] *= (1 - alpha * 0.6)
        bg_arr = np.clip(bg_arr, 0, 255).astype(np.uint8)
        bg = Image.fromarray(bg_arr, 'RGB')
    else:
        for y in range(H):
            for x in range(W):
                alpha = rf_pixels[x, y] / 255.0
                r, g, b = bg.getpixel((x, y))
                bg.putpixel((x, y), (
                    int(r * (1 - alpha * 0.6)),
                    int(g * (1 - alpha * 0.6)),
                    int(b * (1 - alpha * 0.6))
                ))

    # 4. 轻微胶片颗粒（随机强度 2~6，每张图不同）
    if HAS_NUMPY:
        grain_std = random.uniform(2, 6)
        grain = np.random.normal(0, grain_std, (H, W, 3)).astype(np.int16)
        bg_arr = np.clip(np.array(bg, dtype=np.int16) + grain, 0, 255).astype(np.uint8)
        bg = Image.fromarray(bg_arr, 'RGB')

    # 5. 封面阴影（随机强度，每张图不同）
    shadow_intensity = random.uniform(0.25, 0.45)
    shadow_full = Image.new('L', (W, H), 0)
    sd = ImageDraw.Draw(shadow_full)
    sd.ellipse([COVER_X - 12, cover_y - 2,
                COVER_X + COVER_SIZE + 12, cover_y + COVER_SIZE + 2], fill=100)
    shadow_full = shadow_full.filter(ImageFilter.GaussianBlur(18))
    bg_arr = np.array(bg, dtype=np.float32)
    shadow_arr = np.array(shadow_full, dtype=np.float32) / 255.0
    for c in range(3):
        bg_arr[:, :, c] *= (1 - shadow_arr * shadow_intensity)
    bg = Image.fromarray(np.clip(bg_arr, 0, 255).astype(np.uint8), 'RGB')

    # 6. 绘制CD装饰（V2原版）
    draw = ImageDraw.Draw(bg)
    draw.ellipse([cd_cx - cd_outer_r, cd_cy - cd_outer_r,
                  cd_cx + cd_outer_r, cd_cy + cd_outer_r],
                 outline=CD_LINE_COLOR, width=CD_BORDER)
    draw.ellipse([cd_cx - CD_INNER_R, cd_cy - CD_INNER_R,
                  cd_cx + CD_INNER_R, cd_cy + CD_INNER_R],
                 outline=CD_LINE_COLOR, width=2)
    draw.ellipse([cd_cx - CD_HOLE_R, cd_cy - CD_HOLE_R,
                  cd_cx + CD_HOLE_R, cd_cy + CD_HOLE_R],
                 fill=(30, 30, 35), outline=CD_LINE_COLOR, width=1)

    # 6. 封面左上角镜面高光（V2原版，修复：不破坏全局alpha）
    gloss = make_cover_gloss(COVER_X, cover_y, COVER_SIZE)
    gloss_rgba = Image.new('RGBA', (W, H), (255, 255, 255, 0))
    gloss_rgba.putalpha(gloss)
    bg = Image.alpha_composite(bg.convert('RGBA'), gloss_rgba).convert('RGB')

    # 7. 粘贴封面
    bg.paste(cover_resized, (COVER_X, cover_y))

    # 8. 封面边框（动态配色）
    draw = ImageDraw.Draw(bg)
    draw.rectangle([COVER_X - 1, cover_y - 1,
                    COVER_X + COVER_SIZE, cover_y + COVER_SIZE],
                   outline=border_color, width=2)

    bg.save(output_path, 'PNG')
    return True


def main():
    parser = argparse.ArgumentParser(description='V3最终版：V2底子+动态配色')
    parser.add_argument('--input', default=None, help='封面源目录')
    parser.add_argument('--output', default=None, help='输出目录')
    parser.add_argument('--test', default=None, help='测试单张图片路径')
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))

    if args.test:
        if not os.path.exists(args.test):
            print(f'[ERROR] 文件不存在: {args.test}')
            sys.exit(1)
        out = args.test.rsplit('.', 1)[0] + '_v3b.png'
        print(f'[TEST] {args.test}')
        ok = process_v3(args.test, out)
        if ok:
            print(f'[OK]  → {out}')
        else:
            print('[FAIL]')
        return

    input_dir = args.input or os.path.join(script_dir, 'cover_sources', 'input')
    output_dir = args.output or os.path.join(script_dir, 'output', 'bg_v3')

    if not os.path.isdir(input_dir):
        print(f'[ERROR] 输入目录不存在: {input_dir}')
        sys.exit(1)
    os.makedirs(output_dir, exist_ok=True)

    exts = ('.jpg', '.jpeg', '.png', '.webp')
    files = sorted(f for f in os.listdir(input_dir)
                   if f.lower().endswith(exts))

    if not files:
        print('[WARN] 输入目录无封面图片')
        sys.exit(0)

    ok = 0
    for i, f in enumerate(files, 1):
        src = os.path.join(input_dir, f)
        name = os.path.splitext(f)[0]
        dst = os.path.join(output_dir, f'bg_v3b_{i:02d}_{name}.png')
        print(f'[{i}/{len(files)}] {f} ...', end=' ')
        if process_v3(src, dst):
            print('OK')
            ok += 1
        else:
            print('SKIP')

    print(f'\n完成: {ok}/{len(files)} 张')


if __name__ == '__main__':
    main()
