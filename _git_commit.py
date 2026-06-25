import subprocess

result = subprocess.run(
    ['git', 'add', '-A'],
    cwd=r'C:\Users\qujt\.qclaw\workspace',
    capture_output=True
)
print('git add:', result.returncode, result.stderr.decode()[:200] if result.stderr else '')

result = subprocess.run(
    ['git', 'commit', '-m', '2026-06-25: 郑源-擦肩而过入库 (artist_id=325, album_id=596)'],
    cwd=r'C:\Users\qujt\.qclaw\workspace',
    capture_output=True
)
print('git commit:', result.returncode)
print(result.stdout.decode())
print(result.stderr.decode()[:300])
