import os, glob

LYRICS = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics'

# 找所有 lrc 文件，按大小排序，显示最大的几个
lrc_files = glob.glob(LYRICS + '/**/*.lrc', recursive=True)
print(f'Total LRC files: {len(lrc_files)}')

# 按大小排序
lrc_files.sort(key=lambda f: os.path.getsize(f), reverse=True)
for f in lrc_files[:5]:
    size = os.path.getsize(f)
    try:
        content = open(f, encoding='utf-8').read()
        lines = [l for l in content.split('\n') if l.strip() and not l.startswith('[')]
        print(f'\n{f}')
        print(f'  Size: {size}b, Non-timestamp lines: {len(lines)}')
        for line in lines[:3]:
            print(f'  > {line}')
    except Exception as ex:
        print(f'\n{f} Error: {ex}')
