import subprocess, os

os.chdir(r'C:\Users\qujt\.qclaw\workspace')

# commit
r = subprocess.run(
    ['git', 'commit', '-m', 'A项目：专辑详情页重构 - 展示曲目列表+外部评分+乐评链接'],
    capture_output=True, text=True, encoding='utf-8'
)
print('STDOUT:', r.stdout)
print('STDERR:', r.stderr)
print('returncode:', r.returncode)
