#!/usr/bin/env python3
import re
import sqlite3

DB = "music"
DRY = False

def norm(s):
    return re.sub(r"\s*,\s*", ",", (s or "").strip())

def nospace(s):
    return re.sub(r"\s+", "", s or "").lower()

def main():
    db = sqlite3.connect(DB)
    db.execute("BEGIN")
    q = db.execute

    genre_rows = q("SELECT genre_id, name FROM genres").fetchall()
    style_rows = q("SELECT style_id, name FROM styles").fetchall()
    artist_rows = q("SELECT artist_id, name, name_variants FROM artists").fetchall()

    gmap = {norm(n): i for i, n in genre_rows}
    gmap2 = {nospace(n): i for i, n in genre_rows}
    smap = {norm(n): i for i, n in style_rows}
    smap2 = {nospace(n): i for i, n in style_rows}
    amap = {n.strip(): i for i, n, _ in artist_rows}
    import json
    for i, n, v in artist_rows:
        try:
            for x in json.loads(v or "[]"):
                amap[x.strip()] = i
        except Exception:
            pass

    single = re.compile(r"^[^,/&]+$")

    def resolve(album_id, value, map1, map2, table, key_col):
        if value is None:
            return None, "-"
        v1 = map1.get(norm(value))
        if v1:
            return v1, "match"
        v2 = map2.get(nospace(value))
        if v2:
            return v2, "match(ws)"
        if single.match((value or "").strip()):
            cur = q(f"SELECT MAX({key_col}) FROM {table}").fetchone()[0] or 0
            new_id = cur + 1
            q(f"INSERT INTO {table} ({key_col}, name) VALUES (?,?)", (new_id, value.strip()))
            map1[norm(value)] = new_id
            map2[nospace(value)] = new_id
            return new_id, "insert"
        return None, "no-match"

    stats = {"genre": 0, "genre_insert": 0, "style": 0, "style_insert": 0,
             "artist": 0, "duration": 0, "region": 0}
    misses = {"genre": [], "style": [], "artist": []}

    for album_id, val in q(
        'SELECT album_id, genre FROM albums WHERE status="active" AND genre<>"" AND genre_id IS NULL'
    ).fetchall():
        gid, how = resolve(album_id, val, gmap, gmap2, "genres", "genre_id")
        if gid:
            q("UPDATE albums SET genre_id=? WHERE album_id=?", (gid, album_id))
            stats["genre"] += 1
            if how == "insert":
                stats["genre_insert"] += 1
        else:
            misses["genre"].append((album_id, val))

    for album_id, val in q(
        'SELECT album_id, style FROM albums WHERE status="active" AND style<>"" AND style_id IS NULL'
    ).fetchall():
        sid, how = resolve(album_id, val, smap, smap2, "styles", "style_id")
        if sid:
            q("UPDATE albums SET style_id=? WHERE album_id=?", (sid, album_id))
            stats["style"] += 1
            if how == "insert":
                stats["style_insert"] += 1
        else:
            misses["style"].append((album_id, val))

    for album_id, artist in q(
        'SELECT album_id, artist FROM albums WHERE status="active" AND artist<>"" AND artist_id IS NULL'
    ).fetchall():
        aid = amap.get(artist.strip())
        if aid:
            q("UPDATE albums SET artist_id=? WHERE album_id=?", (aid, album_id))
            stats["artist"] += 1
        else:
            misses["artist"].append((album_id, artist))

    dur_targets = q(
        'SELECT album_id, duration FROM albums WHERE status="active" '
        'AND (duration IS NULL OR duration="" OR duration GLOB "*:*:*" OR duration LIKE "%min%")'
    ).fetchall() + [(r[0], None) for r in q(
        'SELECT album_id FROM albums WHERE status="active" AND duration GLOB "[0-9]*" AND duration NOT GLOB "*:*"'
    ).fetchall()]
    seen = set()
    for album_id, _ in dur_targets:
        if album_id in seen:
            continue
        seen.add(album_id)
        rows = q("SELECT COUNT(*), COUNT(duration), COALESCE(SUM(duration),0) FROM tracks WHERE album_id=?", (album_id,)).fetchone()
        total, withdur, summs = rows
        if total > 0 and total == withdur:
            secs = summs // 1000
            new = f"{secs // 60}:{secs % 60:02d}"
            q("UPDATE albums SET duration=? WHERE album_id=?", (new, album_id))
            stats["duration"] += 1

    seta = {n.strip(): r for i, n, r in db.execute("SELECT artist_id,name,region FROM artists")}
    import json as _j
    for i, n, v, r in db.execute("SELECT artist_id,name,name_variants,region FROM artists"):
        if r:
            seta.setdefault(n.strip(), r)
            try:
                for x in _j.loads(v or "[]"):
                    seta.setdefault(x.strip(), r)
            except Exception:
                pass
    for album_id, artist, artist_id in q(
        'SELECT album_id, artist, artist_id FROM albums WHERE status="active" AND (region IS NULL OR region="")'
    ).fetchall():
        r = None
        if artist_id and artist_id:
            rr = q("SELECT region FROM artists WHERE artist_id=?", (artist_id,)).fetchone()
            if rr and rr[0]:
                r = rr[0]
        if not r:
            r = seta.get(artist.strip())
        if r:
            q("UPDATE albums SET region=? WHERE album_id=?", (r, album_id))
            stats["region"] += 1

    if DRY:
        db.rollback()
        print("DRY-RUN (已回滚)")
    else:
        db.commit()
        print("EXECUTED (已提交)")
    print("genre_id:", stats["genre"], "(插入新行", stats["genre_insert"], ")")
    print("style_id:", stats["style"], "(插入新行", stats["style_insert"], ")")
    print("artist_id:", stats["artist"])
    print("duration:", stats["duration"])
    print("region:", stats["region"])
    print()
    print("未匹配 genre:", len(misses["genre"]))
    for aid, v in misses["genre"][:30]:
        print("  ", aid, v)
    print("未匹配 style:", len(misses["style"]))
    for aid, v in misses["style"][:30]:
        print("  ", aid, v)
    print("未匹配 artist:", len(misses["artist"]))
    for aid, v in misses["artist"][:30]:
        print("  ", aid, v)

if __name__ == "__main__":
    main()