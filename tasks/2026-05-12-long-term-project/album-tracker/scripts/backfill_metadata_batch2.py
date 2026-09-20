#!/usr/bin/env python3
import os
import re
import sys
import time
import sqlite3
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fill_missing_tracks import (
    http_get,
    json_loads_or_none,
    s2,
    has_chinese,
    album_match,
    artist_match,
    itunes_find,
    qq_find,
    ne_find,
    UA,
    NE_H,
)

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "music")

counters = {"year": 0, "country": 0, "genre": 0, "style": 0,
            "company": 0, "mbid": 0}


def itunes_meta(cid):
    url = f"https://itunes.apple.com/lookup?id={cid}"
    d = json_loads_or_none(http_get(url, timeout=40))
    if not d:
        return None
    for it in d.get("results", []):
        if it.get("wrapperType") == "collection":
            return it
    return None


def ne_meta(aid):
    url = f"http://music.163.com/api/album/{aid}"
    d = json_loads_or_none(http_get(url, headers=NE_H))
    if not d or d.get("code") != 200:
        return None
    return d.get("album") or {}


def mb_release_group_meta(album_name, artist):
    q = urllib.parse.quote(f'release:"{album_name}" AND artist:"{artist}"')
    url = f"https://musicbrainz.org/ws/2/release-group?query={q}&inc=releases&fmt=json&limit=5"
    d = json_loads_or_none(http_get(url, headers={"User-Agent": UA["User-Agent"] + " (backfill)"}))
    time.sleep(1.1)
    if not d:
        return None
    rg = None
    for g in d.get("release-groups", []):
        if album_match(album_name, g.get("title")):
            rg = g
            break
    if not rg:
        rg = (d.get("release-groups") or [None])[0]
    if not rg:
        return None
    rels = rg.get("releases") or []
    best = None
    for x in rels:
        if album_match(album_name, x.get("title")):
            best = x
            break
    if best is None:
        best = rels[0] if rels else None
    return {
        "date": rg.get("first-release-date"),
        "release_id": best.get("id") if best else None,
        "country": best.get("country") if best else None,
        "label": (best.get("label-info") or [{}])[0].get("label", {}).get("name") if best and best.get("label-info") else None,
    }


def fmt_year(v):
    if not v:
        return None
    m = re.search(r"\d{4}", str(v))
    return int(m.group(0)) if m else None


def clean_company(c):
    if not c:
        return None
    c = s2(str(c)).strip()
    c = re.sub(r"^[℗©]", "", c).strip()
    c = re.sub(r"^\(\s*[PC]\s*\)", "", c, flags=re.I).strip()
    c = re.sub(r"^[0-9]{4}\s*", "", c)
    if c.lower() in ("explicit", "clean"):
        return None
    return c[:80] or None


def run_mbid_phase(db):
    q = db.execute
    rows = q("""
        SELECT a.album_id, a.album_name, a.artist FROM albums a
        WHERE a.status='active' AND (a.release_mbid IS NULL OR a.release_mbid='')
        ORDER BY a.album_id
    """).fetchall()
    print(f"mbid待处理 {len(rows)}", flush=True)
    t0 = time.time()
    for i, (aid, an, ar) in enumerate(rows):
        meta = mb_release_group_meta(an, ar)
        if meta and meta.get("release_id"):
            q("UPDATE albums SET release_mbid=? WHERE album_id=?", (meta["release_id"], aid))
            counters["mbid"] += 1
        if meta and meta.get("date"):
            y = fmt_year(meta.get("date"))
            if y:
                r2 = q("SELECT 1 FROM albums WHERE album_id=? AND release_year IS NOT NULL AND release_year>0", (aid,)).fetchone()
                if not r2:
                    q("UPDATE albums SET release_year=? WHERE album_id=?", (y, aid))
                    counters["year"] += 1
        if meta and meta.get("country"):
            q("UPDATE albums SET country=? WHERE album_id=? AND (country IS NULL OR country='')", (meta["country"], aid))
            counters["country"] += 1
        if meta and meta.get("label"):
            lab = clean_company(meta["label"])
            if lab:
                q("UPDATE albums SET release_company=? WHERE album_id=? AND (release_company IS NULL OR release_company='')", (lab, aid))
                counters["company"] += 1
        db.commit()
        if (i + 1) % 10 == 0:
            print(f"mbid进度 {i+1}/{len(rows)}", flush=True)
        if time.time() - t0 > 2400:
            print("mbid阶段超时")
            break


def run_meta_phase(db, limit):
    q = db.execute
    rows = q("""
        SELECT a.album_id, a.album_name, a.artist FROM albums a
        WHERE a.status='active' AND (
             (a.genre IS NULL OR a.genre='')
          OR (a.style IS NULL OR a.style='')
          OR (a.release_company IS NULL OR a.release_company='')
          OR (a.release_year IS NULL OR a.release_year=0)
        )
        ORDER BY a.album_id
    """).fetchall()
    if limit:
        rows = rows[:limit]
    print(f"meta待处理 {len(rows)}", flush=True)
    for i, (aid, an, ar) in enumerate(rows):
        need = q("SELECT release_year, genre, style, release_company FROM albums WHERE album_id=?", (aid,)).fetchone()
        need_year, need_genre, need_style, need_comp = (
            need[0] in (None, 0), not need[1], not need[2], not need[3])
        if not (need_year or need_genre or need_style or need_comp):
            continue
        cid = itunes_find(an, ar)
        neid = ne_find(an, ar)
        im = itunes_meta(cid) if cid else None
        nm = ne_meta(neid) if neid else None
        if im:
            if need_year:
                y = fmt_year(im.get("releaseDate"))
                if y:
                    q("UPDATE albums SET release_year=? WHERE album_id=?", (y, aid))
                    counters["year"] += 1
            if need_genre:
                g = (im.get("primaryGenreName") or "").strip()
                if g:
                    q("UPDATE albums SET genre=? WHERE album_id=?", (g, aid))
                    counters["genre"] += 1
            if need_style and not has_chinese(an + ar):
                g = (im.get("primaryGenreName") or "").strip()
                if g and not re.search(r"[,\/]", g):
                    q("UPDATE albums SET style=? WHERE album_id=?", (g, aid))
                    counters["style"] += 1
            if need_comp:
                c = clean_company(im.get("copyright"))
                if c:
                    q("UPDATE albums SET release_company=? WHERE album_id=?", (c, aid))
                    counters["company"] += 1
        if nm:
            if need_year:
                y = fmt_year(nm.get("publishTime"))
                if y:
                    q("UPDATE albums SET release_year=? WHERE album_id=?", (y, aid))
                    counters["year"] += 1
            if need_comp:
                c = clean_company(nm.get("company"))
                if c:
                    q("UPDATE albums SET release_company=? WHERE album_id=?", (c, aid))
                    counters["company"] += 1
        db.commit()
        if (i + 1) % 10 == 0:
            print(f"meta进度 {i+1}/{len(rows)}", flush=True)


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    phase = sys.argv[2] if len(sys.argv) > 2 else "all"
    db = sqlite3.connect(DB, timeout=60)
    q = db.execute

    rows = q("""
        SELECT a.album_id, ar.country FROM albums a
        JOIN artists ar ON ar.artist_id = a.artist_id
        WHERE a.status='active' AND (a.country IS NULL OR a.country='')
          AND ar.country IS NOT NULL AND ar.country NOT IN ('', 'XX')
    """).fetchall()
    for aid, c in rows:
        q("UPDATE albums SET country=? WHERE album_id=?", (c, aid))
        counters["country"] += 1
    db.commit()
    print("country从artists表抄", counters["country"])

    if phase in ("all", "mbid"):
        run_mbid_phase(db)
    if phase in ("all", "meta"):
        run_meta_phase(db, limit)

    db.close()
    print("=== 批次2结束 ===")
    for k, v in counters.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()