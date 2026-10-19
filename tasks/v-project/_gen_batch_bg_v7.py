#!/usr/bin/env python3
"""V7 · 深夜唱片内封。1920×1080 PNG；保留封面 x=180 / 550px。

python3 _gen_batch_bg_v7.py --test 'cover.jpg'
python3 _gen_batch_bg_v7.py --input cover_sources/input/歌单 --output output/bg_v7/歌单

只读输入，独立输出。无网络、字体或新增依赖；Pillow + NumPy。
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

W, H = 1920, 1080
COVER_X, COVER_SIZE = 180, 550
COVER_Y = (H - COVER_SIZE) // 2
EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}


def load_cover(path: Path) -> Image.Image:
    """Correct EXIF, flatten transparency, and retain the established square crop."""
    with Image.open(path) as source:
        source = ImageOps.exif_transpose(source).convert('RGBA')
        flattened = Image.new('RGBA', source.size, (23, 24, 25, 255))
        flattened.alpha_composite(source)
        return ImageOps.fit(flattened.convert('RGB'), (COVER_SIZE, COVER_SIZE),
                            method=Image.Resampling.LANCZOS)


def palette(cover: Image.Image) -> tuple[np.ndarray, np.ndarray]:
    """Population-weighted chromatic colour, avoiding white/black dominance."""
    small = np.asarray(cover.resize((80, 80)), dtype=np.float32).reshape(-1, 3)
    lum = small @ np.array([.2126, .7152, .0722], dtype=np.float32)
    chroma = small.max(axis=1) - small.min(axis=1)
    usable = small[(lum > 28) & (lum < 224) & (chroma > 18)]
    if len(usable) < 80:
        usable = small[(lum > 20) & (lum < 238)]
    if len(usable) < 20:
        usable = small
    bins, counts = np.unique((usable // 32).astype(np.int16), axis=0, return_counts=True)
    dominant_bin = bins[np.argmax(counts)]
    group = usable[np.all((usable // 32).astype(np.int16) == dominant_bin, axis=1)]
    colour = group.mean(axis=0)
    neutral = float(colour @ np.array([.2126, .7152, .0722]))
    ambient = np.clip(neutral * .64 + colour * .36, 35, 205)
    accent = np.clip(neutral * .25 + colour * .75, 65, 215)
    return ambient, accent


def background(cover: Image.Image, ambient: np.ndarray, rng: np.random.Generator) -> Image.Image:
    """Smooth directional light and fine monochrome grain; quiet title-safe right half."""
    y, x = np.mgrid[:H, :W].astype(np.float32)
    light = np.exp(-(((x - 435) / 620) ** 2 + ((y - 400) / 560) ** 2))
    lower = np.exp(-(((x - 780) / 760) ** 2 + ((y - 960) / 330) ** 2))
    arr = np.empty((H, W, 3), dtype=np.float32)
    arr[:] = (14, 16, 18)
    arr += light[..., None] * (ambient * .28 + np.array([8, 7, 6]))
    arr += lower[..., None] * ambient * .075
    # A very soft memory of the source, rather than a stretched visible duplicate.
    memory = ImageOps.fit(cover, (480, 270)).filter(ImageFilter.GaussianBlur(48)).resize((W, H))
    arr += (np.asarray(memory, dtype=np.float32) - 100) * .025 * light[..., None]
    vignette = np.clip(((x - 780) / 1500) ** 2 + ((y - 500) / 1100) ** 2, 0, 1)
    arr *= (1 - vignette * .2)[..., None]
    right = np.clip((x - 1050) / 700, 0, 1)
    right = right * right * (3 - 2 * right)
    arr *= (1 - .3 * right)[..., None]
    # Achromatic grain avoids coloured speckles, including in dark encodes.
    arr += rng.normal(0, .68, (H, W, 1)).astype(np.float32)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def shadow(canvas: Image.Image, box: tuple, radius: int, opacity: int) -> None:
    mask = Image.new('L', canvas.size)
    ImageDraw.Draw(mask).rectangle(box, fill=opacity)
    mask = mask.filter(ImageFilter.GaussianBlur(radius))
    canvas.paste((0, 0, 0), (0, 0, W, H), mask)


def disc(accent: np.ndarray) -> Image.Image:
    """A partly sleeved, realistically lit record. The cover never gets recoloured."""
    size = 642
    y, x = np.mgrid[:size, :size].astype(np.float32)
    cx = cy = (size - 1) / 2
    dx, dy = x - cx, y - cy
    r = np.sqrt(dx * dx + dy * dy)
    theta = np.arctan2(dy, dx)
    grooves = np.sin(r * 3.25) * 1.45 + np.sin(r * 1.08) * .65
    sheen = np.exp(-(np.sin(theta - .65) / .27) ** 2) * 15
    edge = np.exp(-((r - 316) / 1.6) ** 2) * 22
    base = 19 + grooves + sheen + edge
    arr = np.repeat(base[..., None], 3, axis=2)
    arr += np.array([-.8, 0, .7], dtype=np.float32)
    label = r < 92
    label_grain = np.sin(x * .7) * .8 + np.sin(y * .94) * .8
    arr[label] = (accent * .6 + 33) + label_grain[label, None]
    ring = (r > 96) & (r < 98)
    arr[ring] = 37
    arr[r < 7] = (12, 14, 16)
    rgba = np.concatenate((np.clip(arr, 0, 255),
                           (np.clip((320 - r) * 255, 0, 255))[..., None]), axis=2)
    return Image.fromarray(rgba.astype(np.uint8))


def render(cover: Image.Image) -> Image.Image:
    # Pixel-based digest: stable between processes and when input files are renamed.
    digest = hashlib.sha256(cover.tobytes()).digest()
    rng = np.random.default_rng(int.from_bytes(digest[:8], 'big'))
    ambient, accent = palette(cover)
    bg = background(cover, ambient, rng)
    # Broad cast shadow followed by local contact shadow.
    shadow(bg, (182, 287, 836, 845), 42, 95)
    record = disc(accent)
    record_mask = Image.new('L', (W, H))
    record_mask.paste(record.getchannel('A'), (424, 231))
    record_mask = record_mask.filter(ImageFilter.GaussianBlur(22))
    bg.paste((0, 0, 0), (0, 0, W, H), record_mask.point(lambda a: int(a * .34)))
    bg = bg.convert('RGBA')
    bg.alpha_composite(record, (414, 219))
    # Sleeve has a matte bevel and a narrow right-hand opening.
    sleeve = Image.new('RGBA', (578, 578), (32, 34, 35, 255))
    sd = ImageDraw.Draw(sleeve)
    rim = tuple(int(v) for v in accent * .22 + 38)
    sd.rectangle((0, 0, 577, 577), outline=(*rim, 255), width=1)
    sd.line((2, 1, 575, 1), fill=(105, 103, 94, 95))
    sd.line((573, 4, 573, 574), fill=(5, 7, 8, 190), width=2)
    bg.alpha_composite(sleeve, (166, 251))
    # Paste source after all lighting, preserving source colours and square geometry.
    bg.paste(cover, (COVER_X, COVER_Y))
    details = ImageDraw.Draw(bg)
    details.line((180, 842, 730, 842), fill=(*tuple(int(v * .19) for v in accent), 255), width=1)
    # Sparse optical registration marks, outside the cover and text-safe area.
    muted = tuple(int(v * .18 + 12) for v in accent)
    for xx, yy, sx, sy in [(148, 233, 1, 1), (762, 847, -1, -1)]:
        details.line((xx, yy, xx + sx * 13, yy), fill=(*muted, 255), width=1)
        details.line((xx, yy, xx, yy + sy * 13), fill=(*muted, 255), width=1)
    return bg.convert('RGB')


def process_v7(source: Path, destination: Path) -> bool:
    if source.resolve() == destination.resolve():
        print(f'[ERROR] 拒绝覆盖输入: {source}', file=sys.stderr)
        return False
    try:
        cover = load_cover(source)
        image = render(cover)
        destination.parent.mkdir(parents=True, exist_ok=True)
        image.save(destination, 'PNG', optimize=True)
        print(f'[OK] {destination}', flush=True)
        return True
    except (OSError, ValueError) as exc:
        print(f'[ERROR] {source}: {exc}', file=sys.stderr, flush=True)
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description='V7 · 深夜唱片内封 / 1920×1080 PNG')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--test', type=Path, help='生成单张；默认也写入独立输出目录')
    mode.add_argument('--input', type=Path, help='批量封面目录，不递归')
    parser.add_argument('--output', type=Path, help='输出目录，默认 output/bg_v7')
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    output = args.output or root / 'output' / 'bg_v7'
    if args.test:
        return 0 if process_v7(args.test, output / f'{args.test.stem}_v7.png') else 1
    source = args.input or root / 'cover_sources' / 'input'
    if not source.is_dir():
        parser.error(f'输入目录不存在: {source}')
    if source.resolve() == output.resolve():
        parser.error('输入与输出目录必须分开')
    files = sorted(p for p in source.iterdir() if p.is_file() and p.suffix.lower() in EXTENSIONS)
    if not files:
        print('[WARN] 目录中没有封面；歌单子目录请用 --input 指定。')
        return 0
    count = sum(process_v7(f, output / f'bg_v7_{i:02d}_{f.stem}.png') for i, f in enumerate(files, 1))
    print(f'完成: {count}/{len(files)}', flush=True)
    return 0 if count == len(files) else 1


if __name__ == '__main__':
    raise SystemExit(main())
