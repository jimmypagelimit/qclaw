import subprocess, os
os.chdir(r'C:\Users\qujt\.qclaw\workspace')
r = subprocess.run(['git', 'push'], capture_output=True, text=True, timeout=300)
print('STDOUT:', r.stdout[-2000:] if len(r.stdout)>2000 else r.stdout)
print('STDERR:', r.stderr[-2000:] if len(r.stderr)>2000 else r.stderr)
print('RC:', r.returncode)
