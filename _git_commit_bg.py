import subprocess, os
os.chdir(r"C:\Users\qujt\.qclaw\workspace")
subprocess.run(["git", "add", "video_thumbs/20th_century_indie_bg/"], check=True)
r = subprocess.run(["git", "commit", "-m", "20th_century_indie_bg: 20 background images (CD style, 1920x1080)"],
                   capture_output=True, text=True)
print(r.stdout)
if r.returncode != 0:
    print("ERR:", r.stderr[-300:])