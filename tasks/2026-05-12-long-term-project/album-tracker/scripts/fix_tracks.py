#!/usr/bin/env python3
"""手动修复指定专辑曲目（人工核对后的源）。
用法: fix_tracks.py 'album_id:qq:albumID|album_id:itunes:collectionId|...'
"""
import sqlite3, os, sys, time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from fill_missing_tracks import itunes_tracks, qq_tracks, mb_release_tracks, ne_tracks, s2

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "music")


def main():
    db = sqlite3.connect(DB)
    for spec in sys.argv[1:]:
        aid_s, src, ref = spec.split(":", 2)
        aid = int(aid_s)
        if src == "qq":
            tracks = qq_tracks(ref)
        elif src == "itunes":
            tracks = itunes_tracks(ref)
        elif src == "mb":
            tracks = mb_release_tracks(ref)
        elif src == "ne":
            tracks = ne_tracks(ref)
        else:
            print(f"[{aid}] unknown src {src}")
            continue
        if not tracks:
            print(f"[{aid}] FAIL no tracks from {src}:{ref}")
            continue
        db.execute("DELETE FROM tracks WHERE album_id=?", (aid,))
        db.executemany(
            "INSERT INTO tracks (album_id, track_number, track_name, duration, disc_number, source) VALUES (?,?,?,?,?,?)",
            [(aid, tn, s2(name), dur, dn, src) for dn, tn, name, dur, src in tracks])
        db.commit()
        print(f"[{aid}] OK {len(tracks)} from {src}")
        time.sleep(0.3)
    db.close()


if __name__ == "__main__":
    main()