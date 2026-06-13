import os, subprocess

# Try http instead and different CDN
urls = [
    "http://is1.mzstatic.com/image/thumb/Music221/v4/b6/4d/93/b64d9383-74b7-9b5f-1706-7d51437da544/196872891805.jpg/600x600bb.jpg",
    "https://a1.mzstatic.com/us/r1000/0/Music221/v4/b6/4d/93/b64d9383-74b7-9b5f-1706-7d51437da544/196872891805.jpg",
]

cover_dir = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers"
cover_name = "458-Natalia_Lafourcade-Hasta_la_raíz.jpg"
cover_path = os.path.join(cover_dir, cover_name)

for url in urls:
    result = subprocess.run([
        "curl", "-k", "-s", "-L", "-o", cover_path, "-w", "HTTP:%{http_code} Size:%{size_download}", url
    ], capture_output=True, text=True, timeout=15)
    status = result.stdout.strip()
    print(f"URL: {url[:60]}... => {status}")
    if os.path.exists(cover_path) and os.path.getsize(cover_path) > 1000:
        print(f"SUCCESS: {os.path.getsize(cover_path)} bytes")
        break
