from PIL import Image
import os

src = r'C:\Users\qujt\.qclaw\workspace\album-tracker\public\covers\sueter7-TodoSalioBien.jpg'
dst = r'C:\Users\qujt\.qclaw\workspace\album-tracker\public\covers\sueter7-TodoSalioBien_600.jpg'

img = Image.open(src)
print('Original size:', img.size)
img_resized = img.resize((600, 600), Image.LANCZOS)
img_resized.save(dst, 'JPEG', quality=85, optimize=True)
size = os.path.getsize(dst)
print(f'Resized to 600x600, saved: {size} bytes ({size/1024:.0f} KB)')

# 覆盖原文件
import shutil
shutil.copy(dst, src)
print('Replaced original')
