#!/usr/bin/env python3
import os
import re
import sys
import time
import json
import sqlite3
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fill_missing_tracks import http_get, json_loads_or_none, has_chinese, norm_album

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "music")
UA_B = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7"}

counters = {"producer": 0, "pitchfork": 0}


def clean_infobox(v):
    v = re.sub(r"<!--.*?-->", "", v, flags=re.S)
    v = re.sub(r"<ref[^>]*>.*?</ref>", "", v, flags=re.S)
    v = re.sub(r"<[^>]+>", "", v)
    # {{...}} templates on same segment: keep last arg display value
    while "{{" in v:
        m = re.search(r"\{\{([^{}]*)\}\}", v)
        if not m:
            break
        inner = m.group(1)
        parts = [p.split("|")[-1] for p in inner.replace("\n", " ").split("{{")] if False else inner.split("|")
        disp = parts[-1].strip() if len(parts) > 1 else ""
        if not disp:
            disp = inner.strip()
        v = v[:m.start()] + disp + v[m.end():]
    v = re.sub(r"\[\[([^\]|]*)\|([^\]]*)\]\]", r"\2", v)
    v = re.sub(r"\[\[([^\]]*)\]\]", r"\1", v)
    v = v.replace("'',", ",").replace("''", "")
    return v.strip()


def wiki_article_titles(title):
    url = ("https://en.wikipedia.org/w/api.php?action=query&list=search"
           f"&srsearch={urllib.parse.quote(title)}&srlimit=5&format=json")
    d = json_loads_or_none(http_get(url, headers=UA_B))
    out = []
    for s in (d or {}).get("query", {}).get("search", []):
        out.append(s.get("title"))
    time.sleep(0.4)
    return out


def wiki_infobox_producer(title):
    """Return producer list from wikipedia wikitext infobox, or None."""
    url = ("https://en.wikipedia.org/w/api.php?action=query&prop=revisions"
           f"&rvprop=content&rvslots=main&format=json&titles={urllib.parse.quote(title)}&redirects=1")
    raw = http_get(url, headers=UA_B)
    if not raw:
        time.sleep(0.4)
        return None
    d = json_loads_or_none(raw)
    pages = (d or {}).get("query", {}).get("pages", {}) or {}
    content = None
    for p in pages.values():
        revs = p.get("revisions") or []
        if revs:
            content = (revs[0].get("slots", {}).get("main", {}) or {}).get("*")
    time.sleep(0.4)
    if not content:
        return None
    m = re.search(r"\|\s*(?:producer|Producer|producers)\s*=\s*(.+?)(?=\n\s*\|\s*[a-zA-Z][a-zA-Z_ ]*=|\Z)", content, flags=re.S)
    if not m:
        return None
    val = m.group(1)
    val = clean_infobox(val)
    vals = []
    for seg in re.split(r"\n\s*\*|\n", val):
        seg = re.sub(r"^\s*\*+\s*", "", seg).strip()
        for part in re.split(r"\s*,\s*", seg):
            part = part.strip()
            if part and part not in vals:
                vals.append(part)
    joined = ", ".join(vals)
    if len(joined) < 2:
        return None
    return joined[:200]


def producer_from_wikipedia(album_name, artist):
    candidates = []
    for t in album_name, f"{album_name} ({artist} album)", f"{album_name} (album)":
        if t:
            candidates.append(t)
    for t in candidates:
        v = wiki_infobox_producer(t)
        if v:
            return v
    # fuzzy search fallback
    hits = wiki_article_titles(f"{album_name} {artist} album")
    for h in hits[:3]:
        v = wiki_infobox_producer(h)
        if v:
            return v
    return None


def pitchfork_meta(album_name, artist):
    q = urllib.parse.quote(f"{artist} {album_name}")
    raw = http_get(f"https://pitchfork.com/search/?query={q}", headers=UA_B)
    if not raw:
        time.sleep(0.5)
        return None
    slugs = re.findall(r"/reviews/albums/([a-z0-9-]+)/", raw)
    if not slugs:
        time.sleep(0.5)
        return None
    na = norm_album(album_name)
    if not na:
        return None
    target = None
    for s in set(slugs):
        if na in norm_album(s):
            target = s
            break
    if not target:
        time.sleep(0.5)
        return None
    time.sleep(0.5)
    page = http_get(f"https://pitchfork.com/reviews/albums/{target}/", headers=UA_B)
    if not page:
        return None
    score = None
    mscore = re.search(r'"reviewScore":\s*"?([\d.]+)"?', page)
    if not mscore:
        mscore = re.search(r'"ratingValue":\s*"?([\d.]+)"?', page)
    if mscore:
        score = float(mscore.group(1))
    return {"score": score, "url": f"https://pitchfork.com/reviews/albums/{target}/"}


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    db = sqlite3.connect(DB, timeout=60)
    rows = db.execute("""
        SELECT a.album_id, a.album_name, a.artist
        FROM albums a
        WHERE a.status='active'
          AND (a.overall_score > 0 OR a.pitchfork_score IS NOT NULL)
          AND ((a.producer IS NULL OR a.producer='')
               OR (a.pitchfork_score IS NULL))
        ORDER BY a.album_id
    """).fetchall()
    if limit:
        rows = rows[:limit]
    print(f"待处理 {len(rows)}", flush=True)
    for i, (aid, an, ar) in enumerate(rows):
        need = db.execute("SELECT producer, pitchfork_score FROM albums WHERE album_id=?", (aid,)).fetchone()
        need_prod = not need[0]
        need_pf = need[1] is None
        if need_prod and not has_chinese(an + ar):
            p = producer_from_wikipedia(an, ar)
            if p and p.lower() not in ("none", "various"):
                db.execute("UPDATE albums SET producer=? WHERE album_id=?", (p, aid))
                counters["producer"] += 1
        elif need_prod:
            # Chinese albums: try zh.wikipedia
            p = producer_from_wikipedia(an, ar)
            if p and p.lower() not in ("none", "various"):
                db.execute("UPDATE albums SET producer=? WHERE album_id=?", (p, aid))
                counters["producer"] += 1
        if need_pf and not has_chinese(an + ar):
            m = pitchfork_meta(an, ar)
            if m:
                db.execute("UPDATE albums SET pitchfork_score=?, review_url=? WHERE album_id=?",
                           (m["score"], m["url"], aid))
                counters["pitchfork"] += 1
        db.commit()
        if (i + 1) % 10 == 0:
            print(f"进度 {i+1}/{len(rows)}", flush=True)
    db.close()
    print("=== 批次3结束 ===")
    for k, v in counters.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()