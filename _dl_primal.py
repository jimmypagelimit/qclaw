import os, urllib.request, ssl, json

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://coverartarchive.org/release/3da3da09-b8af-42f4-b432-fd768268f5c3"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
try:
    resp = urllib.request.urlopen(req, timeout=10, context=ctx)
    data = json.loads(resp.read())
    imgs = data.get("images", [])
    if imgs:
        front = [i for i in imgs if i.get("front")]
        img_url = (front[0] if front else imgs[0]).get("image", "")
        req2 = urllib.request.Request(img_url, headers={"User-Agent": "Mozilla/5.0"})
        img_data = urllib.request.urlopen(req2, timeout=10, context=ctx).read()
        out = r"C:\Users\qujt\.qclaw\workspace\video_thumbs\20th_century_indie\14_Primal Scream_Velocity Girl.jpg"
        with open(out, "wb") as f:
            f.write(img_data)
        print(f"OK: {len(img_data)//1024} KB")
    else:
        print("no images in CAA response")
except Exception as e:
    print(f"error: {e}")