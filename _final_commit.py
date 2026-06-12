import subprocess, os

os.chdir(r'C:\Users\qujt\.qclaw\workspace')

# 1. Add all remaining changes
print('1. Adding remaining changes...')
r = subprocess.run(['git', 'add', '-A'], capture_output=True, encoding='utf-8', errors='ignore')
print(f'  git add: {r.returncode}')

# 2. Commit
print('2. Committing...')
msg = 'chore: 清理临时文件，更新记忆文档\n\n- 删除85个临时数据库和脚本文件\n- 更新 TOOLS.md（数据库路径规则）\n- 更新 memory/2026-06-12.md\n- 清理 RYM 抓取的临时图片和JSON'
r2 = subprocess.run(['git', 'commit', '-m', msg], capture_output=True, encoding='utf-8', errors='ignore')
print(f'  git commit: {r2.returncode}')
if r2.returncode != 0:
    print(f'  stderr: {r2.stderr[:200]}')
else:
    print(f'  stdout: {r2.stdout[:100]}')

# 3. Push
print('\n3. Pushing...')
r3 = subprocess.run(['git', 'push'], capture_output=True, encoding='utf-8', errors='ignore')
print(f'  Push exit code: {r3.returncode}')
if r3.returncode == 0:
    print('  Push success!')
else:
    print(f'  stderr: {r3.stderr[:200]}')

# 4. Delete self
print('\n4. Cleaning up...')
try:
    os.remove('_final_commit.py')
    print('  Deleted self')
except:
    pass

print('\nAll done!')
