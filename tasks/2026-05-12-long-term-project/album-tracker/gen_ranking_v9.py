"""
Album Ranking Image Generator - Final v9
CD-style album card with info layout

Usage:
  python gen_ranking.py --album "Album Name" --artist "Artist" --year 1983 \
       --cover /path/to/cover.jpg --output output.png [options]

Options:
  --album     Album name (required)
  --artist    Artist name (required, English only, no translation)
  --year      Release year (required)
  --rank      Ranking number (optional, shown as No.XX)
  --date      Release date YYYY-MM (default: year-01)
  --rating    RYM rating (default: "")
  --ratings   RYM ratings count (default: "")
  --genres-en Genres in English (default: "")
  --genres-cn Genres in Chinese (default: "")
  --now-playing Currently playing song (default: "")
  --cover     Path to cover image file (required)
  --output    Output path (default: output.png)
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import math
import argparse
import os

OUTPUT_DIR = r'C:\Users\15206\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\ranking-images'


def generate(
    album_name,
    artist,
    release_year,
    cover_path,
    output_path=None,
    rank=None,
    release_date=None,
    rym_rating="",
    rym_ratings_count="",
    genres_en="",
    genres_cn="",
    now_playing=""
):
    """Generate a CD-style ranking image."""
    
    # Load cover
    if os.path.exists(cover_path):
        cover = Image.open(cover_path).convert('RGB')
    else:
        raise FileNotFoundError(f"Cover not found: {cover_path}")
    
    # Defaults
    if not release_date:
        release_date = f"{release_year}-01"
    if not output_path:
        safe_name = f"{release_year}_{artist.replace(' ', '_')}_{album_name.replace(' ', '_')[:20]}.png"
        output_path = os.path.join(OUTPUT_DIR, safe_name)
    
    # Create canvas
    canvas = Image.new('RGB', (1920, 1080), (18, 18, 20))
    
    # Background: blurred cover
    bg = cover.resize((2200, 1237), Image.LANCZOS).filter(ImageFilter.GaussianBlur(radius=90))
    bg = ImageEnhance.Brightness(bg).enhance(0.35)
    left = (2200 - 1920) // 2
    top = (1237 - 1080) // 2
    bg = bg.crop((left, top, left + 1920, top + 1080))
    canvas.paste(bg, (0, 0))
    
    canvas = canvas.convert('RGBA')
    draw = ImageDraw.Draw(canvas)
    
    # === CD-style cover ===
    cd_size = 440
    cover_cd = cover.resize((cd_size, cd_size), Image.LANCZOS)
    
    cd_layer = Image.new('RGBA', (cd_size + 16, cd_size + 16), (0, 0, 0, 0))
    cd_draw = ImageDraw.Draw(cd_layer)
    
    # Outer ring - silver
    cd_draw.ellipse([0, 0, cd_size + 16, cd_size + 16], fill=(180, 180, 185, 255))
    cd_draw.ellipse([4, 4, cd_size + 12, cd_size + 12], fill=(150, 150, 155, 255))
    cd_draw.ellipse([8, 8, cd_size + 8, cd_size + 8], fill=(200, 200, 205, 255))
    
    # Paste cover
    cd_layer.paste(cover_cd, (8, 8))
    
    # Center hole
    center = cd_size // 2 + 8
    for r in range(35, 50):
        alpha = int(180 * (1 - abs(r - 42) / 8))
        cd_draw.ellipse([center - r, center - r, center + r, center + r],
                        fill=(80, 80, 85, alpha))
    
    # Shine effect
    shine = Image.new('RGBA', (cd_size + 16, cd_size + 16), (255, 255, 255, 0))
    for y in range(cd_size // 3):
        for x in range(0, cd_size + 16, 2):
            dist = math.sqrt((x - cd_size//2)**2 + (y - cd_size//3)**2)
            if dist < cd_size // 2:
                alpha = int(25 * (1 - y / (cd_size // 3)))
                s_draw = ImageDraw.Draw(shine)
                s_draw.point((x, y), fill=(255, 255, 255, alpha))
    cd_layer = Image.alpha_composite(cd_layer, shine)
    
    # Position CD
    cd_x, cd_y = 220, 300
    
    # Shadow
    shadow = Image.new('RGBA', (cd_size + 40, cd_size + 40), (0, 0, 0, 90))
    canvas.paste(shadow, (cd_x - 15, cd_y - 10), shadow)
    canvas.paste(cd_layer, (cd_x, cd_y), cd_layer)
    
    # === Fonts ===
    try:
        font_title = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 56)
        font_album = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 44)
        font_label = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 24)
        font_value = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 24)
        font_now = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 21)
    except Exception as e:
        print(f"Font warning: {e}")
        font_title = font_album = font_label = font_value = font_now = ImageFont.load_default()
    
    # === Text Layout ===
    text_x = cd_x + cd_size + 70
    text_start_y = 260
    
    # Title line: Year or Rank
    if rank:
        title_text = f"No.{rank}"
    else:
        title_text = f"{release_year}"
    draw.text((text_x, text_start_y), title_text, font=font_title, fill=(255, 255, 255, 255))
    
    # Album name
    draw.text((text_x, text_start_y + 75), album_name, font=font_album, fill=(255, 255, 255, 255))
    
    # Info block
    info_y = text_start_y + 145
    line_height = 38
    
    def draw_info_line(y, label, value=""):
        draw.text((text_x + 20, y), label, font=font_label, fill=(240, 240, 245, 255))
        if value:
            lw = len(label) * 12 + 8
            draw.text((text_x + 20 + lw, y), value, font=font_value, fill=(210, 210, 215, 255))
        return y + line_height
    
    # Artist (English only!)
    info_y = draw_info_line(info_y, f"艺术家：{artist}")
    
    # Release date
    info_y = draw_info_line(info_y, f"发行日：{release_date}")
    
    # RYM rating
    if rym_rating:
        rating_str = f"RYM评分：{rym_rating}"
        if rym_ratings_count:
            rating_str += f" from {rym_ratings_count} ratings"
        info_y = draw_info_line(info_y, rating_str)
    
    # Genres
    if genres_en:
        info_y = draw_info_line(info_y, f"Genres：{genres_en}")
    
    # Style (Chinese)
    if genres_cn:
        info_y = draw_info_line(info_y, f"风格：{genres_cn}")
    
    # Now playing
    if now_playing:
        draw.text((70, 55), f"正在播放：{now_playing}", font=font_now, fill=(255, 255, 255, 200))
        draw.line([(70, 88), (340, 88)], fill=(255, 255, 255, 50), width=1)
    
    # Save
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    canvas = canvas.convert('RGB')
    canvas.save(output_path, 'PNG', quality=95)
    print(f"Saved: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description='Album Ranking Image Generator v9')
    parser.add_argument('--album', required=True, help='Album name')
    parser.add_argument('--artist', required=True, help='Artist name (English)')
    parser.add_argument('--year', required=True, type=int, help='Release year')
    parser.add_argument('--cover', required=True, help='Path to cover image')
    parser.add_argument('--output', default='', help='Output path')
    parser.add_argument('--rank', type=int, help='Ranking number')
    parser.add_argument('--date', default='', help='Release date YYYY-MM')
    parser.add_argument('--rating', default='', help='RYM rating')
    parser.add_argument('--ratings', default='', help='RYM ratings count')
    parser.add_argument('--genres-en', default='', help='Genres in English')
    parser.add_argument('--genres-cn', default='', help='Genres in Chinese')
    parser.add_argument('--now-playing', default='', help='Currently playing song')
    
    args = parser.parse_args()
    
    generate(
        album_name=args.album,
        artist=args.artist,
        release_year=args.year,
        cover_path=args.cover,
        output_path=args.output or None,
        rank=args.rank,
        release_date=args.date or None,
        rym_rating=args.rating,
        rym_ratings_count=args.ratings,
        genres_en=args.genres_en,
        genres_cn=args.genres_cn,
        now_playing=args.now_playing
    )


if __name__ == '__main__':
    main()
