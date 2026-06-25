import os, subprocess

AT = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker'

# List dist files
dist = os.path.join(AT, 'dist')
if os.path.exists(dist):
    for f in os.listdir(dist):
        print(f)

# Run CLI help
print('---')
import subprocess
out = subprocess.run(['node', 'dist/cli.js', '--help'], cwd=AT, capture_output=True, text=True, timeout=15)
print('stdout:', out.stdout)
print('stderr:', out.stderr)
