import subprocess
import os

os.chdir(r'C:\Users\qujt\.qclaw\workspace')

# Commit
r = subprocess.run(['git', 'commit', '-m', 'add album covers (484 images, 62MB) + update HEARTBEAT/memory'], capture_output=True, text=True)
print('STDOUT:', r.stdout)
print('STDERR:', r.stderr)
print('RC:', r.returncode)

# Push
if r.returncode == 0:
    r2 = subprocess.run(['git', 'push'], capture_output=True, text=True)
    print('PUSH STDOUT:', r2.stdout)
    print('PUSH STDERR:', r2.stderr)
    print('PUSH RC:', r2.returncode)
