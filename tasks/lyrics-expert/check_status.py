import os, glob

root = r"C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics"
tracklists = r"C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\tracklists"

# lyrics
files = glob.glob(os.path.join(root, "**", "*.*"), recursive=True)
txts = [f for f in files if f.endswith(".txt")]
lrcs = [f for f in files if f.endswith(".lrc")]
bilingual = [f for f in files if "_bilingual" in f]

# artists
artists = set()
for f in files:
    rel = os.path.relpath(f, root)
    parts = rel.split(os.sep)
    if len(parts) >= 2:
        artists.add(parts[0])

# albums per artist
print(f"Lyrics total: {len(files)} files")
print(f"  TXT: {len(txts)}, LRC: {len(lrcs)}, Bilingual: {len(bilingual)}")
print(f"  Artists: {len(artists)}")

for a in sorted(artists):
    a_dir = os.path.join(root, a)
    albums = [d for d in os.listdir(a_dir) if os.path.isdir(os.path.join(a_dir, d))]
    a_files = [f for f in files if f.startswith(a_dir)]
    print(f"  {a}: {len(albums)} albums, {len(a_files)} files")

# tracklists
tl_files = glob.glob(os.path.join(tracklists, "**", "*.*"), recursive=True)
print(f"\nTracklists: {len(tl_files)} files")
for f in sorted(tl_files):
    print(f"  {os.path.relpath(f, tracklists)}")

# chosen.txt
chosen = os.path.join(root, "_chosen.txt")
if os.path.exists(chosen):
    with open(chosen, "r", encoding="utf-8") as fh:
        print(f"\n_chosen.txt ({sum(1 for _ in fh)} entries - needs re-read)")
