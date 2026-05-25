import subprocess, os

result = subprocess.run(
    ["git", "status", "--porcelain", "video_thumbs/"],
    capture_output=True, text=True, cwd=r"C:\Users\qujt\.qclaw\workspace"
)
print(result.stdout.strip() or "(clean)")