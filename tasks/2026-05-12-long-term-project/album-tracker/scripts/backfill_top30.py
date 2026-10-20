#!/usr/bin/env python3
"""2026收听TOP30元数据补全：producer(Wikipedia) + genre/style(iTunes) + mbid(MB)"""
import os, re, sys, time, sqlite3, urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fill_missing_tracks import http_get, json_loads_or_none, has_chinese, album_match, itunes_find, UA
from backfill_metadata_batch3 import producer_from_wikipedia
from backfill_metadata_batch2 import mb_release_group_meta, itunes_meta

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "music")
TOP30 = [682,409,458,520,555,511,554,424,516,507,517,542,565,59,323,374,382,386,431,461,468,488,500,506,523,543,547,548,617,661]
c = {"producer":0,"genre":0,"style":0,"mbid":0,"skip":0}

db = sqlite3.connect(DB, timeout=60)
q = db.execute
for aid in TOP30:
    row = q("SELECT album_name, artist, genre, style, producer, release_mbid FROM albums WHERE album_id=?", (aid,)).fetchone()
    if not row:
        continue
    an, ar, genre, style, producer, mbid = row
    need_p, need_g, need_s, need_m = not producer, not genre, not style, not mbid
    if not (need_p or need_g or need_s or need_m):
        c["skip"] += 1
        continue
    print(f"[{aid}] {ar} - {an}  p={need_p} g={need_g} s={need_s} m={need_m}", flush=True)
    # mbid
    if need_m:
        meta = mb_release_group_meta(an, ar)
        if meta and meta.get("release_id"):
            q("UPDATE albums SET release_mbid=? WHERE album_id=?", (meta["release_id"], aid))
            c["mbid"] += 1
            print(f"  +mbid {meta['release_id']}", flush=True)
    # genre/style via iTunes
    if need_g or need_s:
        cid = itunes_find(an, ar)
        im = itunes_meta(cid) if cid else None
        if im:
            g = (im.get("primaryGenreName") or "").strip()
            if g and need_g:
                q("UPDATE albums SET genre=? WHERE album_id=?", (g, aid))
                c["genre"] += 1
                print(f"  +genre {g}", flush=True)
            if g and need_s and not has_chinese(an + ar) and not re.search(r"[,/]", g):
                q("UPDATE albums SET style=? WHERE album_id=?", (g, aid))
                c["style"] += 1
                print(f"  +style {g}", flush=True)
    # producer via wikipedia
    if need_p:
        p = producer_from_wikipedia(an, ar)
        if p and p.lower() not in ("none", "various"):
            q("UPDATE albums SET producer=? WHERE album_id=?", (p, aid))
            c["producer"] += 1
            print(f"  +producer {p}", flush=True)
    db.commit()
db.close()
print("=== done ===", c)
