import urllib.request, json, os

playlist_id = "17965216587"
songs = [
    ("Never Meant MV", "16502162", "American Football"),
    ("The Dull Fool", "17549215", "Neutral Milk Hotel"),
    ("Tegseth Like God's Shoeshine", "4175535", "Modest Mouse"),
    ("Get Me... I'm Dying", "16805309", "Belle & Sebastian"),
    ("Little League", "2341346", "Cap'n Jazz"),
    ("Gold Sweet... MV", "18295907", "Pavement"),
    ("Katyo Song", "18812194", "Red House Painters"),
    ("Medicine Bottle", "18812244", "Red House Painters"),
    ("When You Sleep", "4174137", "My Bloody Valentine"),
    ("Velouria", "18319252", "Pixies"),
    ("Debaser", "18319264", "Pixies"),
    ("Where Is My Mind?", "4236643", "Pixies"),
    ("Little Fury Things", "2427833", "Dinosaur Jr."),
    ("Velocity Girl", "26782095", "Primal Scream"),
    ("Just Like Honey", "21965464", "The Jesus and Mary Chain"),
    ("Will He Kiss Me Tonight", "1824960753", "Dolly Mixture"),
    ("This Can't Be Today", "2099448567", "Rain Parade"),
    ("Only a Shadow", "1304563548", "The Cleaners From Venus"),
    ("Silly Girl", "21882074", "Television Personalities"),
    ("Sob TV Story", "1327278224", "The Beach Bullies"),
]

out_dir = r"C:\Users\qujt\.qclaw\workspace\video_thumbs\20th_century_indie"
os.makedirs(out_dir, exist_ok=True)

def get_album_cover(song_id):
    url = f"https://music.163.com/api/song/detail/?ids=[{song_id}]"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        songs_data = data.get("songs", [])
        if songs_data:
            album = songs_data[0].get("album", {})
            album_name = album.get("name", "unknown")
            artist = songs_data[0].get("artists", [{}])[0].get("name", "unknown")
            cover_url = album.get("picUrl", "")
            return album_name, artist, cover_url
    except Exception as e:
        print(f"  error: {e}")
    return None, None, None

results = []
for i, (name, sid, artist) in enumerate(songs, 1):
    print(f"[{i}/20] {artist} - {name}")
    album_name, alb_artist, cover_url = get_album_cover(sid)
    if cover_url:
        # download
        try:
            req = urllib.request.Request(cover_url, headers={"User-Agent": "Mozilla/5.0"})
            resp = urllib.request.urlopen(req, timeout=10)
            img_data = resp.read()
            safe_name = f"{i:02d}_{artist.replace('/', '_')}_{name.replace('/', '_')[:30]}.jpg"
            out_path = os.path.join(out_dir, safe_name)
            with open(out_path, "wb") as f:
                f.write(img_data)
            sz = len(img_data) // 1024
            print(f"  OK: {out_path} ({sz} KB)")
            results.append((out_path, album_name or name, alb_artist or artist))
        except Exception as e:
            print(f"  download error: {e}")
    else:
        print(f"  no cover found")

print(f"\nDone. {len(results)}/{len(songs)} covers saved.")