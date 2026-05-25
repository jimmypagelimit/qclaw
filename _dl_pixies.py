import urllib.request, json, os

sid = "4236643"
url = f"https://music.163.com/api/song/detail/?ids=[{sid}]"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
resp = urllib.request.urlopen(req, timeout=10)
data = json.loads(resp.read())
song = data["songs"][0]
album_name = song["album"]["name"]
artist = song["artists"][0]["name"]
cover_url = song["album"]["picUrl"]
print(f"{artist} - {album_name}")
print(f"cover: {cover_url}")

out_dir = r"C:\Users\qujt\.qclaw\workspace\video_thumbs\20th_century_indie"
req2 = urllib.request.Request(cover_url, headers={"User-Agent": "Mozilla/5.0"})
img = urllib.request.urlopen(req2, timeout=10).read()
out_path = os.path.join(out_dir, "12_Pixies_Where Is My Mind.jpg")
with open(out_path, "wb") as f:
    f.write(img)
print(f"saved: {out_path} ({len(img)//1024} KB)")