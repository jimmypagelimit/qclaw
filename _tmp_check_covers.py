import os

# 检查封面文件
covers_dir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers'

files_to_check = [
    '382-Car Seat Headrest-Teens of Denial.jpg',
    '547-Car Seat Headrest-Teen of Denial (Joes Story).jpg',
    '554-Car Seat Headrest-Teens of Style.jpg'
]

print('封面文件检查:')
for fname in files_to_check:
    fpath = os.path.join(covers_dir, fname)
    if os.path.exists(fpath):
        size = os.path.getsize(fpath)
        print(f'  [OK] {fname} ({size} bytes)')
    else:
        print(f'  [MISSING] {fname}')

# 列出所有含 Car Seat Headrest 的封面
print('\n所有 Car Seat Headrest 封面:')
if os.path.exists(covers_dir):
    for f in sorted(os.listdir(covers_dir)):
        if 'Car Seat' in f or 'carseat' in f.lower() or 'Carseat' in f:
            print(f'  {f}')
else:
    print(f'  [ERROR] covers目录不存在: {covers_dir}')
