import subprocess, os

os.chdir(r"C:\Users\qujt\.qclaw\workspace")
result = subprocess.run(["git", "push"], capture_output=True, text=True, timeout=180)
print(result.stdout[-2000:])
if result.returncode != 0:
    print("STDERR:", result.stderr[-500:])