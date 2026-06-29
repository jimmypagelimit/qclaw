"""
_gen_batch_bg_v3.py — V3精致版（修复版）

相对V2的改进：
1. 黑胶纹理（Perlin噪声）
2. CD彩虹反光
3. 使用痕迹（划痕+磨损+指纹）
4. 封面质感（纸纹+环境光）
5. 动态配色（从封面提取主色）
6. 椭圆暗角（NumPy加速）

用法:
    python _gen_batch_bg_v3_fixed.py [--input DIR] [--test FILE]
"""

import os, sys, math, random, argparse
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print('[WARN] NumPy未安装，将使用慢速版')

try:
    from noise import pnoise2
    HAS_NOISE = True
except ImportError:
    HAS_NOISE = False
    print('[WARN] noise库未安装，将使用伪噪声')

try:
    import colorsys
    HAS_COLORSYS = True
except ImportError:
    HAS_COLORSYS = False
    print('[WARN] colorsys未安装，将使用简化HSV')

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance


# ── 参数 ─────────────────────────────────────────────────
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

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


# ── 工具函数 ─────────────────────────────────────────────

def hsv_to_rgb_simple(h, s, v):
    """简化HSV→RGB（无colorsys时使用）"""
    if HAS_COLORSYS:
        r, g, b = colorsys.hsv_to_rgb(h/360, s, v)
        return int(r*255), int(g*255), int(b*255)
    else:
        # 简化版
        c = v * s
        x = c * (1 - abs((h/60) % 2 - 1))
        m = v - c
        if h < 60:
            r, g, b = c, x, 0
        elif h < 120:
            r, g, b = x, c, 0
        elif h < 180:
            r, g, b = 0, c, x
        elif h < 240:
            r, g, b = 0, x, c
        elif h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        return int((r+m)*255), int((g+m)*255), int((b+m)*255)


def extract_dominant_color(cover_img, k=3):
    """从封面提取主色（k-means）"""
    if not HAS_NUMPY:
        return (212, 175, 55)
    try:
        small = cover_img.copy().resize((50, 50), Image.LANCZOS)
        arr = np.array(small, dtype=np.float32)
        pixels = arr.reshape(-1, 3)
        # 随机初始化中心
        idx = np.random.choice(len(pixels), k, replace=False)
        centers = pixels[idx]
        for _ in range(5):
            dists = np.linalg.norm(pixels[:, None] - centers, axis=2)
            labels = np.argmin(dists, axis=1)
            for i in range(k):
                if np.any(labels == i):
                    centers[i] = pixels[labels == i].mean(axis=0)
        brightest = max(centers, key=lambda c: np.mean(c))
        return tuple(int(c) for c in brightest)
    except:
        return (212, 175, 55)


def make_vinyl_texture(w, h, cx, cy, radius):
    """黑胶纹理（Perlin噪声，径向密度）"""
    tex = Image.new('L', (w, h), 0)
    if HAS_NOISE:
        scale = 0.015
        for y in range(h):
            for x in range(w):
                dist = math.sqrt((x-cx)**2 + (y-cy)**2)
                if dist < radius:
                    density = 1.0 - (dist/radius)*0.6
                    n = pnoise2(x*scale*density, y*scale*density, octaves=2)
                    val = int((n+1)*127.5)
                    tex.putpixel((x, y), val)
    else:
        import random as rng
        pixels = [rng.randint(0, 35) for _ in range(w*h)]
        tex.putdata(pixels)
    tex = tex.filter(ImageFilter.GaussianBlur(2))
    return tex


def make_cd_iridescence(w, h, cx, cy, r_outer):
    """CD彩虹反光"""
    irr = Image.new('RGBA', (w, h), (0,0,0,0))
    draw = ImageDraw.Draw(irr)
    offset = random.uniform(-25, 25)
    for deg in range(0, 360, 3):
        angle = math.radians(deg + offset)
        x1 = int(cx + (r_outer-25)*math.cos(angle))
        y1 = int(cy + (r_outer-25)*math.sin(angle))
        x2 = int(cx + (r_outer+8)*math.cos(angle))
        y2 = int(cy + (r_outer+8)*math.sin(angle))
        hue = (deg + offset) % 360
        r, g, b = hsv_to_rgb_simple(hue, 0.4, 0.85)
        if 0<=x1<w and 0<=y1<h and 0<=x2<w and 0<=y2<h:
            draw.line([x1,y1,x2,y2], fill=(r,g,b,25), width=2)
    irr = irr.filter(ImageFilter.GaussianBlur(10))
    return irr


def add_scratches(img):
    """添加轻微划痕"""
    img_rgba = img.convert('RGBA')
    draw = ImageDraw.Draw(img_rgba)
    n = random.randint(1, 2)
    for _ in range(n):
        x1 = random.randint(COVER_X-30, COVER_X+COVER_SIZE+30)
        y1 = random.randint(0, H)
        length = random.randint(80, 300)
        angle = math.radians(random.uniform(-20, 20))
        x2 = int(x1 + length*math.cos(angle))
        y2 = int(y1 + length*math.sin(angle))
        draw.line([x1,y1,x2,y2], fill=(255,255,255,12), width=2)
    return img_rgba.convert('RGB')


def add_corner_wear(img):
    """角落磨损"""
    img_rgba = img.convert('RGBA')
    sz = random.randint(60, 120)
    corner = Image.new('L', (sz, sz), 0)
    d = ImageDraw.Draw(corner)
    for y in range(sz):
        for x in range(sz):
            dist = math.sqrt((x-sz)**2 + (y-sz)**2)
            if dist < sz:
                v = int(255*(1-dist/sz))
                d.point((x,y), v)
    corner = corner.filter(ImageFilter.GaussianBlur(12))
    cimg = Image.new('RGBA', (W,H), (0,0,0,0))
    cimg.paste(corner, (W-sz, H-sz))
    return Image.alpha_composite(img_rgba, cimg).convert('RGB')


def add_cover_paper_texture(cover):
    """封面纸纹"""
    if not HAS_NUMPY:
        return cover
    try:
        arr = np.array(cover, dtype=np.float32)
        noise = np.random.normal(0, 2.5, arr.shape).astype(np.float32)
        arr = np.clip(arr + noise*0.015, 0, 255)
        return Image.fromarray(arr.astype(np.uint8))
    except:
        return cover


def make_vignette_v3(w, h, strength=0.72):
    """椭圆暗角（NumPy加速）"""
    if HAS_NUMPY:
        y, x = np.ogrid[:h, :w]
        cx, cy = w/2, h/2
        dx = (x - cx) / (w * 0.55)
        dy = (y - cy) / (h * 0.45)
        d = np.sqrt(dx**2 + dy**2)
        d = np.clip(d, 0, 1)
        v = (1 - strength*(1-d))*255
        return Image.fromarray(v.astype(np.uint8), 'L')
    else:
        img = Image.new('L', (w,h), 255)
        draw = ImageDraw.Draw(img)
        cx, cy = w//2, h//2
        for y in range(h):
            for x in range(w):
                dx = (x-cx)/(w*0.55)
                dy = (y-cy)/(h*0.45)
                d = math.sqrt(dx**2+dy**2)
                d = min(1.0, max(0.0, d))
                v = int(255*(1-strength*(1-d)))
                draw.point((x,y), v)
        return img


def process_v3(cover_path, output_path):
    """V3主流程"""
    try:
        cover = Image.open(cover_path).convert('RGB')
    except Exception as e:
        print(f'  [SKIP] {e}')
        return False

    cover_y = (H - COVER_SIZE) // 2
    cd_cx = COVER_X + COVER_SIZE // 2
    cd_cy = cover_y + COVER_SIZE // 2
    cd_outer_r = COVER_SIZE // 2 + CD_BORDER

    # 1. 模糊背景
    bg = cover.copy().resize((W, H))
    bg = bg.filter(ImageFilter.GaussianBlur(28))

    # 2. 黑胶纹理
    vinyl_tex = make_vinyl_texture(W, H, cd_cx, cd_cy, cd_outer_r+40)
    tex_overlay = Image.new('RGBA', (W,H), (128,128,128,0))
    tex_overlay.putalpha(vinyl_tex)
    bg = Image.alpha_composite(bg.convert('RGBA'), tex_overlay).convert('RGB')

    # 3. 椭圆暗角
    vig = make_vignette_v3(W, H, 0.72)
    bg.putalpha(vig)
    bg_final = Image.new('RGB', (W,H), (0,0,0))
    bg_final.paste(bg, (0,0), bg)
    bg = bg_final

    # 4. CD彩虹反光
    irr = make_cd_iridescence(W, H, cd_cx, cd_cy, cd_outer_r)
    bg = Image.alpha_composite(bg.convert('RGBA'), irr).convert('RGB')

    # 5. 绘制CD装饰圈
    draw = ImageDraw.Draw(bg)
    draw.ellipse([cd_cx-cd_outer_r, cd_cy-cd_outer_r,
                  cd_cx+cd_outer_r, cd_cy+cd_outer_r],
                 outline=CD_LINE_COLOR, width=CD_BORDER)
    draw.ellipse([cd_cx-CD_INNER_R, cd_cy-CD_INNER_R,
                  cd_cx+CD_INNER_R, cd_cy+CD_INNER_R],
                 outline=CD_LINE_COLOR, width=2)
    draw.ellipse([cd_cx-CD_HOLE_R, cd_cy-CD_HOLE_R,
                  cd_cx+CD_HOLE_R, cd_cy+CD_HOLE_R],
                 fill=(30,30,35), outline=CD_LINE_COLOR, width=1)

    # 6. 右上角圆点（动态配色）
    dom_color = extract_dominant_color(cover)
    for i in range(3):
        dx = DOT_TOP + i*(DOT_RADIUS*2+DOT_GAP)
        draw.ellipse([W-dx-DOT_RADIUS, DOT_TOP,
                      W-dx+DOT_RADIUS, DOT_TOP+DOT_RADIUS*2],
                     fill=dom_color)

    # 7. 封面处理
    sz = min(cover.size)
    left = (cover.width - sz)//2
    top = (cover.height - sz)//2
    cover_sq = cover.crop((left, top, left+sz, top+sz))
    cover_resized = cover_sq.resize((COVER_SIZE, COVER_SIZE), Image.LANCZOS)
    cover_textured = add_cover_paper_texture(cover_resized)
    bg.paste(cover_textured, (COVER_X, cover_y))

    # 8. 封面边框
    draw.rectangle([COVER_X-1, cover_y-1,
                    COVER_X+COVER_SIZE, cover_y+COVER_SIZE],
                   outline=dom_color, width=2)

    # 9. 使用痕迹
    bg = add_scratches(bg)
    bg = add_corner_wear(bg)

    bg.save(output_path, 'PNG')
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default=None)
    parser.add_argument('--output', default=None)
    parser.add_argument('--test', default=None)
    args = parser.parse_args()

    if args.test:
        if not os.path.exists(args.test):
            print(f'[ERROR] 文件不存在: {args.test}')
            sys.exit(1)
        out = args.test.replace('.jpg','_v3.png').replace('.jpeg','_v3.png')
        print(f'[TEST] {args.test}')
        if process_v3(args.test, out):
            print(f'[OK] {out}')
        else:
            print('[FAIL]')
        return

    inp = args.input or os.path.join(SCRIPT_DIR, 'cover_sources', 'input')
    out = args.output or os.path.join(SCRIPT_DIR, 'output', 'bg_v3')
    if not os.path.isdir(inp):
        print(f'[ERROR] 输入目录不存在: {inp}')
        sys.exit(1)
    os.makedirs(out, exist_ok=True)

    exts = ('.jpg','.jpeg','.png','.webp')
    files = sorted(f for f in os.listdir(inp) if f.lower().endswith(exts))
    if not files:
        print('[WARN] 无封面图片')
        sys.exit(0)

    ok = 0
    for i, f in enumerate(files, 1):
        src = os.path.join(inp, f)
        name = os.path.splitext(f)[0]
        dst = os.path.join(out, f'bg_v3_{i:02d}_{name}.png')
        print(f'[{i}/{len(files)}] {f} ...', end=' ')
        if process_v3(src, dst):
            print('OK')
            ok += 1
        else:
            print('FAIL')

    print(f'\n完成: {ok}/{len(files)}')
    print('V3新增: 黑胶纹理 / CD反光 / 使用痕迹 / 动态配色 / 椭圆暗角')


if __name__ == '__main__':
    main()
