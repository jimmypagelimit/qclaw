"""_gen_video_bg_v6.py — V6 深夜电台艺术版

基于 V5 构图（左黑胶唱片 + 中心封面 + 斜向唱针 + 右侧留白 + 黑金氛围），
按高级艺术化提示词重构：

- 背景：暗金色环境光从左侧唱片区域缓慢扩散，向右沉入近乎纯黑（不再是均匀渐变）
- 质感：极细胶片颗粒、模拟噪点、老式 CRT 扫描线、暗角、空气中灰尘感（全部克制）
- 唱片：真实细腻纹路、微弱高光、边缘反射、同心圆细节，静静悬浮在黑暗空间
- 封面：轻微纸张纹理、旧印刷质感、柔和暗金色光晕 → 视觉核心
- 唱针：金属质感、真实机械结构、极简、斜线构图，从左下视觉中心向上延伸
- 右侧：音频波形/频谱残影/老式均衡器刻度抽象图形，细、克制、微微发光、轻微不规则
- 动态：唱片极慢旋转（3秒1圈无缝）、唱针微弱机械抖动、暗金光晕缓慢呼吸、
        右侧频谱轻微跳动、胶片噪点 + 模拟信号闪烁，整体慢、平滑、自然循环

用法:
    python _gen_video_bg_v6.py --test 封面路径
    python _gen_video_bg_v6.py --input DIR --output DIR
"""

import os, sys, math, random, argparse, subprocess, tempfile, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# ═══════════════════════════════════════════════════
# 参数
# ═══════════════════════════════════════════════════
W, H = 1920, 1080
COVER_X = 200
VINYL_DIAMETER = 500
COVER_DIAMETER = 300
VINYL_RING = (VINYL_DIAMETER - COVER_DIAMETER) // 2
VINYL_HOLE_R = 8

# 动画参数（自循环）
FPS = 24
DURATION = 3.0
TOTAL_FRAMES = int(FPS * DURATION)
ROTATION_SPEED = 360 / DURATION       # 3秒转1圈 = 120°/s → 极慢 + 无缝
PULSE_SPEED = 0.8                      # 暗金光晕呼吸频率
EQ_CYCLES = [2, 3, 4, 5, 3, 2]        # 频谱每柱周期（整数→无缝）
BG_ZOOM_AMPLITUDE = 0.012              # 背景微动幅度（更克制）
BG_ZOOM_CYCLES = 1

# 光源参数：暗金色从唱片中心向右衰减
LIGHT_CENTER_X = COVER_X + VINYL_DIAMETER * 0.6   # 光源中心（唱片区域）
LIGHT_CENTER_Y = H // 2
LIGHT_FALLOFF = 620                    # 光衰减半径（越大扩散越远）
LIGHT_BASE_COLOR = (168, 128, 66)      # 暗金


def extract_dominant_color(img):
    small = img.copy().resize((50, 50)).convert('RGB')
    pixels = np.array(small).reshape(-1, 3)
    median = np.median(pixels, axis=0).astype(int)
    return tuple(median)


def make_environment_light():
    """暗金色环境光：左侧光源向右衰减沉入纯黑"""
    y, x = np.ogrid[:H, :W]
    dx = x - LIGHT_CENTER_X
    dy = y - LIGHT_CENTER_Y
    d = np.sqrt(dx * dx + dy * dy)
    # 指数衰减 + 右侧额外衰减（光沉入黑暗）
    falloff = np.exp(-d / LIGHT_FALLOFF)
    right_dim = np.clip((W - x) / (W * 0.65), 0, 1)  # 右侧渐暗
    light = falloff * (0.25 + 0.75 * right_dim)

    # 构建暗金RGB
    r = np.clip(LIGHT_BASE_COLOR[0] * light, 0, 255)
    g = np.clip(LIGHT_BASE_COLOR[1] * light, 0, 255)
    b = np.clip(LIGHT_BASE_COLOR[2] * light, 0, 255)
    rgb = np.stack([r, g, b], axis=-1).astype(np.uint8)
    return rgb


def make_vignette(w, h, strength=0.55):
    y, x = np.ogrid[:h, :w]
    cx, cy = w / 2, h / 2
    rx, ry = w * 0.70, h * 0.62
    d = np.sqrt(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2)
    d = np.clip(d, 0, 1)
    alpha = (1 - np.clip(1 - d, 0, 1) ** 2) * strength
    return (alpha * 255).astype(np.uint8)


def create_base_layers(cover_path):
    """创建静态底层（背景环境光、唱片、封面、唱针基座等）"""
    cover = Image.open(cover_path).convert('RGB')
    dom_color = extract_dominant_color(cover)
    border_color = dom_color

    rand_seed = hash(cover_path) % 10000
    random.seed(rand_seed)
    color_temp = random.uniform(-8, 8)
    grain_std = random.uniform(1.5, 3.5)

    # ── 1. 环境光背景（深黑 + 暗金光源）──
    env = make_environment_light()
    # 极轻微的色温偏移
    if color_temp > 0:
        env[:, :, 0] = np.clip(env[:, :, 0] * (1 + color_temp / 120), 0, 255)
        env[:, :, 2] = np.clip(env[:, :, 2] * (1 - color_temp / 200), 0, 255)
    else:
        env[:, :, 0] = np.clip(env[:, :, 0] * (1 + color_temp / 200), 0, 255)
        env[:, :, 2] = np.clip(env[:, :, 2] * (1 - color_temp / 120), 0, 255)
    bg = Image.fromarray(env.astype(np.uint8))

    # 暗角
    vig = make_vignette(W, H, 0.55)
    bg_arr = np.array(bg, dtype=np.float32)
    vig_arr = vig[:, :, None].astype(np.float32)
    bg_arr = bg_arr * (1 - vig_arr / 255)
    bg = Image.fromarray(bg_arr.astype(np.uint8))

    # 极淡背景纹理（大尺度云状亮度变化）
    cloud = np.random.RandomState(rand_seed).normal(0, 4, (H // 4, W // 4, 1)).astype(np.uint8)
    cloud_img = Image.fromarray(cloud[:, :, 0], 'L').resize((W, H), Image.BICUBIC)
    cloud = np.array(cloud_img, dtype=np.float32)[:, :, None]
    bg_arr = np.array(bg, dtype=np.float32) + cloud
    bg = Image.fromarray(np.clip(bg_arr, 0, 255).astype(np.uint8))

    return bg, cover, dom_color, border_color, grain_std


def build_vinyl_layer(cover, dom_color, border_color, rotation_deg):
    """构建旋转唱片（真实细腻：纹路、高光、边缘反射）"""
    vr = VINYL_DIAMETER // 2
    cr = COVER_DIAMETER // 2
    cx = cy = vr

    vinyl = Image.new('RGBA', (VINYL_DIAMETER, VINYL_DIAMETER), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vinyl)

    # 黑胶底色（深黑偏冷，带渐变）
    vd.ellipse([0, 0, VINYL_DIAMETER - 1, VINYL_DIAMETER - 1],
               fill=(16, 14, 18))

    # 细腻纹路：多层同心圆，越靠外越密集
    for i in range(1, 40):
        r = vr - i * (VINYL_RING / 40)
        if r < cr:
            break
        # 纹路在唱片外圈区域（从封面边缘到唱片边缘）
        alpha = max(2, 12 - i * 0.25)
        shade = int(alpha)
        vd.ellipse([vr - r, vr - r, vr + r, vr + r],
                   outline=(shade, shade - 1, shade + 2), width=1)

    # 封面（纸张纹理 + 旧印刷质感）
    cover_resized = cover.copy().resize((COVER_DIAMETER, COVER_DIAMETER), Image.LANCZOS)
    # 纸张噪点纹理
    paper = np.random.RandomState(42).normal(0, 6, (COVER_DIAMETER, COVER_DIAMETER, 3))
    cover_arr = np.array(cover_resized, dtype=np.float32) + paper
    cover_textured = Image.fromarray(np.clip(cover_arr, 0, 255).astype(np.uint8))

    # 裁成圆形
    mask = Image.new('L', (COVER_DIAMETER, COVER_DIAMETER), 0)
    md = ImageDraw.Draw(mask)
    md.ellipse([0, 0, COVER_DIAMETER - 1, COVER_DIAMETER - 1], fill=255)
    cover_masked = Image.new('RGBA', (COVER_DIAMETER, COVER_DIAMETER), (0, 0, 0, 0))
    cover_masked.paste(cover_textured, (0, 0), mask)
    vinyl.paste(cover_masked, (VINYL_RING, VINYL_RING))

    # 封面边缘：暗金色细环（柔和光晕感）
    vd.ellipse([VINYL_RING - 1, VINYL_RING - 1,
                VINYL_DIAMETER - VINYL_RING, VINYL_DIAMETER - VINYL_RING],
               outline=(140, 108, 56), width=2)
    inner = VINYL_RING + 2
    vd.ellipse([inner, inner, VINYL_DIAMETER - inner - 1, VINYL_DIAMETER - inner - 1],
               outline=(45, 38, 30), width=1)

    # 中心孔
    vd.ellipse([cx - VINYL_HOLE_R, cy - VINYL_HOLE_R,
                cx + VINYL_HOLE_R, cy + VINYL_HOLE_R],
               fill=(10, 8, 12))

    # 边缘反射（左侧微弱亮弧 = 环境光反射）
    edge_glow = Image.new('RGBA', (VINYL_DIAMETER, VINYL_DIAMETER), (0, 0, 0, 0))
    eg = ImageDraw.Draw(edge_glow)
    eg.arc([6, 6, VINYL_DIAMETER - 7, VINYL_DIAMETER - 7],
           start=250, end=320, fill=(168, 128, 66, 26), width=3)
    edge_glow = edge_glow.filter(ImageFilter.GaussianBlur(2))
    vinyl = vinyl.convert('RGBA')
    vinyl.alpha_composite(edge_glow)

    # 旋转
    vinyl_rotated = vinyl.rotate(rotation_deg, expand=False, resample=Image.BICUBIC)

    # 表面高光（极淡，随唱片旋转的扫光）
    highlight = Image.new('RGBA', (VINYL_DIAMETER, VINYL_DIAMETER), (0, 0, 0, 0))
    hd = ImageDraw.Draw(highlight)
    light_angle = rotation_deg * 0.5
    for offset in range(-14, 15):
        angle = light_angle + offset * 0.6
        a = max(0, 5 - abs(offset) * 0.35)
        if a <= 0:
            continue
        hd.pieslice([0, 0, VINYL_DIAMETER - 1, VINYL_DIAMETER - 1],
                     start=angle - 1, end=angle + 1,
                     fill=(255, 235, 200, int(a)))
    highlight = highlight.filter(ImageFilter.GaussianBlur(5))
    highlight_rotated = highlight.rotate(rotation_deg, expand=False, resample=Image.BICUBIC)
    vinyl_rotated = vinyl_rotated.convert('RGBA')
    vinyl_rotated.alpha_composite(highlight_rotated)

    return vinyl_rotated


def draw_tonearm(frame, cx, cy, vr, pulse_factor, frame_idx):
    """精致金属唱针：斜线构图，从视觉中心向上延伸，极简机械结构"""
    draw = ImageDraw.Draw(frame)

    # 唱臂路径：底座在唱片右上方，臂斜向延伸到唱片中部
    base_x = cx + vr + 70
    base_y = cy - vr - 40
    # 唱臂中段（弯曲点）
    mid_x = cx + vr * 0.45
    mid_y = cy - vr * 0.25
    # 唱头位置
    head_x = cx + vr * 0.10
    head_y = cy + vr * 0.10

    # 微弱机械抖动（极慢、极小）
    jitter = math.sin(frame_idx / FPS * 0.8) * 0.6

    # 唱臂阴影
    draw.line([base_x + 4, base_y + 4, mid_x + 4, mid_y + 4],
              fill=(0, 0, 0, 100), width=6)
    draw.line([mid_x + 4, mid_y + 4, head_x + 4, head_y + 4],
              fill=(0, 0, 0, 100), width=5)

    # 唱臂主体（金属渐变：深灰 → 亮银 → 深灰）
    draw.line([base_x, base_y, mid_x, mid_y],
              fill=(70, 66, 72), width=5)
    draw.line([mid_x, mid_y, head_x + jitter, head_y + jitter],
              fill=(75, 70, 78), width=4)
    # 金属高光（上部细亮线）
    draw.line([base_x - 1, base_y - 2, mid_x - 1, mid_y - 2],
              fill=(150, 145, 155), width=1)
    draw.line([mid_x - 1, mid_y - 2, head_x - 1 + jitter, head_y - 2 + jitter],
              fill=(140, 135, 148), width=1)

    # 唱头（极简小方块 + 针尖）
    hs = 12
    head_angle = math.atan2(head_y - mid_y, head_x - mid_x)
    hx = head_x - math.cos(head_angle) * 6
    hy = head_y - math.sin(head_angle) * 6
    draw.polygon([
        (hx, hy),
        (hx + math.cos(head_angle + math.pi/2) * hs * 0.55,
         hy + math.sin(head_angle + math.pi/2) * hs * 0.55),
        (hx + math.cos(head_angle) * hs,
         hy + math.sin(head_angle) * hs),
        (hx + math.cos(head_angle - math.pi/2) * hs * 0.55,
         hy + math.sin(head_angle - math.pi/2) * hs * 0.55),
    ], fill=(55, 52, 58))
    # 针尖（小亮点）
    draw.ellipse([head_x - 1.5, head_y - 1.5, head_x + 1.5, head_y + 1.5],
                 fill=(200, 195, 205))

    # 底座（金属圆座）
    draw.ellipse([base_x - 14, base_y - 14, base_x + 14, base_y + 14],
                 fill=(45, 42, 48), outline=(90, 85, 95), width=2)
    draw.ellipse([base_x - 6, base_y - 6, base_x + 6, base_y + 6],
                 fill=(75, 70, 80))
    draw.ellipse([base_x - 2, base_y - 2, base_x + 2, base_y + 2],
                 fill=(140, 135, 148))


def draw_spectrum(frame, dom_color, border_color, frame_idx):
    """右侧频谱残影：细线、克制、微微发光、轻微不规则（老式均衡器/无线电）"""
    draw = ImageDraw.Draw(frame)
    cx = COVER_X + VINYL_DIAMETER // 2
    cy = H // 2
    vr = VINYL_DIAMETER // 2

    # 频谱区：唱片右侧，垂直居中
    eq_x = COVER_X + VINYL_DIAMETER + 40
    eq_y = cy - vr + 40
    eq_h = vr * 2 - 80
    num_bars = len(EQ_CYCLES)
    bar_w = 3
    bar_gap = 8
    t = frame_idx / FPS

    # 频谱颜色：暗金发光（比封面主色更克制）
    base = (168, 128, 66)

    for i in range(num_bars):
        w = 2 * math.pi * EQ_CYCLES[i] / DURATION
        # 不规则感：多个不同频率叠加 + 轻微相位
        v = (0.5 + 0.5 * math.sin(w * t)) * 0.55 \
            + (0.5 + 0.5 * math.sin(w * 1.7 * t + i * 1.3)) * 0.3 \
            + (0.5 + 0.5 * math.sin(w * 0.6 * t + i * 2.1)) * 0.15
        bar_height = int(eq_h * (0.08 + 0.92 * v))
        bar_y = eq_y + (eq_h - bar_height) // 2
        x0 = eq_x + i * (bar_w + bar_gap)

        # 柱身（细线，暗金，带透明度感）
        glow_alpha = 90 + int(60 * v)
        for layer in range(3):
            lw = bar_w + layer * 4
            alpha = max(0, glow_alpha - layer * 35)
            if alpha <= 0:
                continue
            glow_color = tuple(int(c * alpha / 255) for c in base)
            draw.rectangle([x0 - layer * 2, bar_y,
                            x0 + lw + layer * 2, bar_y + bar_height],
                           fill=(*glow_color,))

        # 顶部亮点（频谱刻度感）
        tip_color = tuple(min(255, int(c * 1.5)) for c in base)
        draw.rectangle([x0, bar_y - 2, x0 + bar_w, bar_y], fill=tip_color)


def add_grain_crt(frame, grain_std, frame_idx):
    """胶片颗粒 + CRT 扫描线 + 灰尘（全部克制）"""
    # 胶片颗粒
    grain = np.random.normal(0, grain_std, (H, W, 3)).astype(np.int16)
    arr = np.array(frame, dtype=np.int16)
    arr = np.clip(arr + grain, 0, 255).astype(np.uint8)
    frame = Image.fromarray(arr)

    # CRT 扫描线（极淡，间隔4px）
    frame = frame.convert('RGBA')
    scan = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scan)
    for y in range(0, H, 4):
        sd.line([(0, y), (W, y)], fill=(0, 0, 0, 8))
    frame.alpha_composite(scan)

    # 灰尘（随机极淡亮点，固定种子但每帧微移）
    rng = np.random.RandomState(1000 + frame_idx * 7)
    dust = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dust)
    for _ in range(14):
        dx = int(rng.uniform(0, W))
        dy = int(rng.uniform(0, H))
        da = int(rng.uniform(3, 12))
        dr = rng.uniform(0.5, 1.8)
        dd.ellipse([dx - dr, dy - dr, dx + dr, dy + dr],
                   fill=(220, 210, 190, da))
    frame.alpha_composite(dust)
    frame = frame.convert('RGB')

    return frame


def render_frame(cover, bg, dom_color, border_color, grain_std,
                 rotation_deg, pulse_factor, frame_idx, bg_zoom):
    """渲染单帧"""
    hw = H // 2
    cx = COVER_X + VINYL_DIAMETER // 2
    cy = hw
    vr = VINYL_DIAMETER // 2

    # 背景微动（极轻微）
    if abs(bg_zoom - 1.0) > 0.001:
        new_w = int(W * bg_zoom)
        new_h = int(H * bg_zoom)
        zoomed = bg.resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - W) // 2
        top = (new_h - H) // 2
        frame = zoomed.crop((left, top, left + W, top + H))
    else:
        frame = bg.copy()

    # 唱片（中层）
    vinyl_layer = build_vinyl_layer(cover, dom_color, border_color, rotation_deg)
    frame = frame.convert('RGBA')
    frame.alpha_composite(vinyl_layer, (COVER_X, cy - vr))
    frame = frame.convert('RGB')

    # 封面暗金光晕（呼吸，视觉核心）
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    glow_r = int(vr * 0.95 * (1 + pulse_factor * 0.12))
    glow_alpha = int(14 + 10 * pulse_factor)
    gd.ellipse([cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r],
               fill=(168, 128, 66, glow_alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(40))
    frame = frame.convert('RGBA')
    frame.alpha_composite(glow)
    frame = frame.convert('RGB')

    # 频谱（右侧，在唱针后面一层）
    draw_spectrum(frame, dom_color, border_color, frame_idx)

    # 唱针（前景层，前于唱片）
    draw_tonearm(frame, cx, cy, vr, pulse_factor, frame_idx)

    # 胶片颗粒 + CRT + 灰尘（最上层）
    frame = add_grain_crt(frame, grain_std, frame_idx)

    return frame


def process_animated(cover_path, output_path):
    print(f'  ⏳ 生成中...', end='', flush=True)
    frames_dir = tempfile.mkdtemp()

    bg, cover, dom_color, border_color, grain_std = create_base_layers(cover_path)

    try:
        for i in range(TOTAL_FRAMES):
            t = i / FPS
            rotation = i * (ROTATION_SPEED / FPS)   # 3秒1圈 → 无缝
            pulse = 0.5 + 0.5 * math.sin(t * 2 * math.pi * PULSE_SPEED)
            bg_zoom = 1.0 + BG_ZOOM_AMPLITUDE * math.sin(2 * math.pi * BG_ZOOM_CYCLES * t / DURATION)

            frame = render_frame(cover, bg, dom_color, border_color, grain_std,
                                 rotation, pulse, i, bg_zoom)
            frame_path = os.path.join(frames_dir, f'frame_{i:04d}.png')
            frame.save(frame_path)

        # MP4
        cmd = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
            '-framerate', str(FPS),
            '-i', os.path.join(frames_dir, 'frame_%04d.png'),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-preset', 'medium',
            '-crf', '18',
            output_path
        ]
        subprocess.run(cmd, check=True, capture_output=True, timeout=120)

        # GIF
        gif_path = output_path.replace('.mp4', '.gif')
        cmd_gif = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
            '-framerate', str(FPS),
            '-i', os.path.join(frames_dir, 'frame_%04d.png'),
            '-vf', 'fps=12,scale=960:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse',
            '-loop', '0',
            gif_path
        ]
        try:
            subprocess.run(cmd_gif, check=True, capture_output=True, timeout=60)
            print(f'✅ MP4+GIF → {os.path.basename(output_path)}', end='')
        except:
            print(f'✅ MP4 → {os.path.basename(output_path)}', end='')
    finally:
        shutil.rmtree(frames_dir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description='V6 深夜电台艺术版')
    parser.add_argument('--input', help='输入目录')
    parser.add_argument('--output', help='输出目录')
    parser.add_argument('--test', help='测试单张')
    args = parser.parse_args()

    if args.test:
        out = args.test.rsplit('.', 1)[0] + '_v6.mp4'
        print(f'[TEST] {args.test}')
        process_animated(args.test, out)
        print(f'\n  → {out}')
        return

    if args.input and args.output:
        os.makedirs(args.output, exist_ok=True)
        covers = sorted([f for f in os.listdir(args.input)
                         if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        total = len(covers)
        for idx, fname in enumerate(covers, 1):
            inp = os.path.join(args.input, fname)
            out_name = fname.rsplit('.', 1)[0] + '_v6.mp4'
            out_path = os.path.join(args.output, out_name)
            print(f'[{idx}/{total}] {fname} ... ', end='', flush=True)
            process_animated(inp, out_path)
            print()
        print(f'\n完成: {total}/{total} 张')
        return

    parser.print_help()


if __name__ == '__main__':
    main()