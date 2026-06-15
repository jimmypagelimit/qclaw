"""
C盘空间分析
"""
import os, shutil, sys

def get_dir_size(path, max_depth=2):
    """快速估算目录大小"""
    total = 0
    try:
        for root, dirs, files in os.walk(path):
            # 计算深度
            depth = root.replace(path, '').count(os.sep)
            if depth > max_depth:
                dirs.clear()  # 不再深入
                continue
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(root, f))
                except:
                    pass
                if total > 1024**3:  # 超过1GB就停止
                    return total
    except:
        pass
    return total

# 检查C盘顶级目录
print('C盘各目录大小（快速估算）:')
print('='*60)

top_dirs = []
for item in os.listdir('C:\\'):
    path = os.path.join('C:\\', item)
    if os.path.isdir(path) and not item.startswith('$'):
        size = get_dir_size(path, max_depth=1)
        if size > 0:
            top_dirs.append((item, size))

# 按大小排序
top_dirs.sort(key=lambda x: x[1], reverse=True)

for name, size in top_dirs[:15]:
    print(f'  {name:<30} {size/1024**3:>6.1f} GB')

print()
print('可清理项:')
print('  1. C:\\Windows\\Temp (系统临时文件)')
print('  2. C:\\Users\\qujt\\AppData\\Local\\Temp (用户临时文件)')
print('  3. C:\\Users\\qujt\\AppData\\Local\\Microsoft\\Windows\\INetCache (IE缓存)')
print('  4. 回收站')
print('  5. 系统还原点 (需用vssadmin)')
print('  6. Windows更新缓存 (需用dism)')
