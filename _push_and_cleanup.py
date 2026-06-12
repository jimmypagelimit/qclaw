import subprocess, os, glob

os.chdir(r'C:\Users\qujt\.qclaw\workspace')

# 1. Verify .gitignore
print('1. Verifying .gitignore...')
with open('.gitignore', 'r', encoding='utf-8') as f:
    content = f.read()
if '_music' in content:
    print('  WARNING: _music still in .gitignore, removing...')
    with open('.gitignore', 'w', encoding='utf-8') as f:
        for line in content.split('\n'):
            if '_music' not in line:
                f.write(line + '\n')
    subprocess.run(['git', 'add', '.gitignore'], check=True)
    subprocess.run(['git', 'commit', '-m', 'chore: 更新 .gitignore 允许跟踪数据库文件'], check=True)
    print('  Fixed and committed')
else:
    print('  OK: _music not in .gitignore')

# 2. Push
print('\n2. Pushing to remote...')
r = subprocess.run(['git', 'push'], capture_output=True, encoding='utf-8', errors='ignore')
print(f'  Push exit code: {r.returncode}')
if r.returncode == 0:
    print('  Push success!')
else:
    print(f'  Push failed: {r.stderr[:200]}')

# 3. Clean up temp files
print('\n3. Cleaning up temp files...')
temp_patterns = [
    '_music*.db',
    '_check_*.py',
    '_git_*.py',
    '_analyze_*.py',
    '_pitchfork_*.py',
    '_pitchfork_*.html',
    'heartbeat-log-*.md',
    'rym_*.json',
    'rym_*.png',
]
cleaned = 0
for pattern in temp_patterns:
    for f in glob.glob(pattern):
        if f != '_music_latest.db':  # Keep the main db
            try:
                os.remove(f)
                cleaned += 1
                print(f'  Deleted: {f}')
            except:
                pass
print(f'  Cleaned {cleaned} temp files')

# 4. Status
print('\n4. Final git status...')
r2 = subprocess.run(['git', 'status', '--short'], capture_output=True, encoding='utf-8', errors='ignore')
if r2.stdout:
    print('  Remaining changes:')
    print('  ' + r2.stdout.replace('\n', '\n  '))
else:
    print('  Working tree clean')

print('\nDone!')
