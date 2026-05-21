from PIL import Image
from collections import Counter

img = Image.open(r'C:\Users\15206\.qclaw\workspace\creature_of_habit_cover.jpg')
print(f'Size: {img.size}')
print(f'Mode: {img.mode}')

# 获取主色调
small = img.resize((50, 50))
pixels = list(small.getdata())
color_counts = Counter(pixels)
top_colors = color_counts.most_common(10)
print('Top 10 colors (RGB):')
for color, count in top_colors:
    print(f'  RGB{color}: {count} pixels')

# 分析图片内容 - 分区域
width, height = img.size
print(f'\nImage analysis (divided into 9 regions):')
for row in range(3):
    for col in range(3):
        left = col * width // 3
        top = row * height // 3
        right = (col + 1) * width // 3
        bottom = (row + 1) * height // 3
        region = img.crop((left, top, right, bottom))
        region_small = region.resize((10, 10))
        region_pixels = list(region_small.getdata())
        avg_color = tuple(int(sum(c[i] for c in region_pixels) / len(region_pixels)) for i in range(3))
        region_name = ['top-left', 'top-center', 'top-right', 'mid-left', 'center', 'mid-right', 'bottom-left', 'bottom-center', 'bottom-right'][row * 3 + col]
        print(f'  {region_name}: avg RGB{avg_color}')
