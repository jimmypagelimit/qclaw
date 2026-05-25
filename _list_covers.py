import os
d = r"C:\Users\qujt\.qclaw\workspace\video_thumbs\20th_century_indie"
files = sorted(os.listdir(d))
for f in files:
    sz = os.path.getsize(os.path.join(d, f)) // 1024
    print(f"{sz:4d} KB  {f}")
print(f"\nTotal: {len(files)} files")