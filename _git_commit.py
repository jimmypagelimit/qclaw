import subprocess, os

os.chdir(r"C:\Users\qujt\.qclaw\workspace")

# git add video_thumbs
subprocess.run(["git", "add", "video_thumbs/20th_century_indie/"], check=True)
print("git add done")

# commit
result = subprocess.run(
    ["git", "commit", "-m", "20th_century_indie: 20 album covers from NME C86 playlist"],
    capture_output=True, text=True
)
print(result.stdout)
if result.returncode != 0:
    print("STDERR:", result.stderr[-500:])