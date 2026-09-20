#!/usr/bin/env python3
"""
补齐缺失专辑曲目 2026-09-18
数据源链: MusicBrainz(mbid) -> iTunes -> QQ音乐 -> MusicBrainz search(兜底)
所有 duration 统一存毫秒。
"""

import sqlite3, json, time, re, urllib.request, urllib.parse, sys, os

try:
    from zhconv import convert as _zhconv_convert
    def s2(name):
        return _zhconv_convert(name, "zh-cn") if name and has_chinese(name) else (name or "")
except ImportError:
    def s2(name):
        return name or ""

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "music")
LOG = "/tmp/opencode/track_fill_log.txt"

UA = {"User-Agent": "album-tracker/1.0 (personal music library)"}
QQ_H = {"Referer": "https://y.qq.com/", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
NE_H = {"Referer": "http://music.163.com", "User-Agent": "Mozilla/5.0"}


def http_get(url, headers=None, timeout=25, retries=2):
    for i in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers or UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:
            if i < retries:
                time.sleep(2)
    return None


def json_loads_or_none(raw):
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except Exception:
        s = raw
        i = s.find("{")
        j = s.rfind("}")
        if i >= 0 and j > i:
            try:
                return json.loads(s[i:j + 1])
            except Exception:
                return None
        return None


def has_chinese(s):
    return bool(re.search(r"[\u4e00-\u9fff]", s or ""))


def norm_album(name):
    n = s2(name).lower()
    n = re.split(r"\s*/\s*", n)[0]
    n = re.sub(r"[\(（].*?[\)）]", "", n)
    n = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", n)
    return n


def norm_artist(name):
    n = s2(name).lower()
    n = re.sub(r"\[.*?\]", "", n)
    n = n.replace("乐队", "").replace("乐团", "").replace("合唱团", "").replace("群星", "").replace("华语", "")
    n = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", n)
    return n


def album_match(a, b):
    a2, b2 = norm_album(a), norm_album(b)
    if not a2 or not b2:
        return False
    return a2 in b2 or b2 in a2


def artist_match(a, b):
    a2, b2 = norm_artist(a), norm_artist(b)
    if not a2 or not b2:
        return False
    if a2 in b2 or b2 in a2:
        return True
    for t in (a2, b2):
        for suf in ("the", "various artists"):
            if t == suf:
                return has_chinese(a) == has_chinese(b)
    return False


def tracks_from_list(items, disc, start_no, name_key, dur_key, dur_div, src):
    out = []
    n = start_no
    for it in items:
        name = it.get(name_key) or it.get(name_key.upper()) or it.get("songname") or it.get("title")
        if not name:
            continue
        names = [name]
        title = it.get("title")
        if title and title != name:
            names = [name, title]
        # keep first non-empty
        dur = it.get(dur_key)
        try:
            dur = int(float(dur)) // dur_div if dur else None
        except Exception:
            dur = None
        out.append((disc, n, name, dur, src))
        n += 1
    return out, n


# ---------------- MusicBrainz ----------------

def mb_release_tracks(mbid):
    url = f"https://musicbrainz.org/ws/2/release/{mbid}?inc=recordings&fmt=json"
    raw = http_get(url, headers={"User-Agent": UA["User-Agent"] + " (muzie)"})
    d = json_loads_or_none(raw)
    if not d or "media" not in d:
        return None
    out = []
    disc = 0
    for med in d.get("media", []):
        disc += 1
        n = 1
        for t in med.get("tracks", []):
            title = t.get("title") or ""
            rec = t.get("recording") or {}
            dur = rec.get("length")
            try:
                dur = int(dur) if dur else None
            except Exception:
                dur = None
            p = t.get("position") or n
            out.append((disc, int(p), title, dur, "musicbrainz"))
            n += 1
    return out or None


def mb_search_tracks(album_name, artist):
    q = urllib.parse.quote(f'release:"{album_name}" AND artist:"{artist}"')
    url = f"https://musicbrainz.org/ws/2/release-group?query={q}&fmt=json&limit=5"
    raw = http_get(url, headers={"User-Agent": UA["User-Agent"] + " (muzie)"})
    d = json_loads_or_none(raw)
    if not d:
        return None
    rg = None
    for g in d.get("release-groups", []):
        title = g.get("title") or ""
        if album_match(album_name, title):
            rg = g
            break
    if not rg:
        rg = (d.get("release-groups") or [None])[0]
    if not rg:
        return None
    gid = rg.get("id")
    url2 = f"https://musicbrainz.org/ws/2/release?release-group={gid}&inc=recordings&fmt=json&limit=5"
    raw2 = http_get(url2, headers={"User-Agent": UA["User-Agent"] + " (muzie)"})
    d2 = json_loads_or_none(raw2)
    if not d2:
        return None
    rel = d2.get("releases") or []
    if not rel:
        return None
    # prefer release matched on title, else first with media
    best = None
    for x in rel:
        if album_match(album_name, x.get("title")):
            best = x
            break
    if best is None:
        best = rel[0]
    mbid = best.get("id")
    time.sleep(1.1)
    return mb_release_tracks(mbid)


def mb_release_tracks_rate_limited(mbid):
    out = mb_release_tracks(mbid)
    time.sleep(1.1)
    return out


# ---------------- iTunes ----------------

def itunes_find(album_name, artist):
    q = urllib.parse.quote(f"{album_name} {artist}")
    url = f"https://itunes.apple.com/search?term={q}&entity=album&limit=15"
    d = json_loads_or_none(http_get(url, timeout=40))
    if not d:
        return None
    for it in d.get("results", []):
        if album_match(album_name, it.get("collectionName")) and artist_match(artist, it.get("artistName")):
            return it.get("collectionId")
    na = norm_album(album_name)
    for it in d.get("results", []):
        if na and norm_album(it.get("collectionName")) == na:
            return it.get("collectionId")
    return None


def itunes_tracks(cid):
    url = f"https://itunes.apple.com/lookup?id={cid}&entity=song&limit=300"
    d = json_loads_or_none(http_get(url, timeout=40))
    if not d:
        return None
    songs = [s for s in d.get("results", []) if s.get("wrapperType") == "track"]
    if not songs:
        return None
    out = []
    for s in songs:
        dn = s.get("discNumber") or 1
        tn = int(s.get("trackNumber") or 0)
        name = s.get("trackName") or ""
        tm = s.get("trackTimeMillis")
        try:
            tm = int(tm) if tm else None
        except Exception:
            tm = None
        out.append((dn, tn, name, tm, "itunes"))
    return out or None


# ---------------- QQ音乐 ----------------

def qq_find(album_name, artist):
    w = f"{album_name} {artist}"
    url = f"https://c.y.qq.com/soso/fcgi-bin/client_search_cp?w={urllib.parse.quote(w)}&p=1&n=10&t=8"
    d = json_loads_or_none(http_get(url, headers=QQ_H))
    if not d:
        return None
    albums = ((d.get("data") or {}).get("album") or {}).get("list") or []
    for a in albums:
        an = s2(a.get("singerName") or "")
        if album_match(album_name, a.get("albumName")) and artist_match(artist, an):
            return a.get("albumID")
    na = norm_album(album_name)
    for a in albums:
        if na and norm_album(a.get("albumName")) == na:
            return a.get("albumID")
    return None


def qq_tracks(aid):
    url = f"https://c.y.qq.com/v8/fcg-bin/fcg_v8_album_info_cp.fcg?albumid={aid}&format=json"
    d = json_loads_or_none(http_get(url, headers=QQ_H))
    if not d:
        return None
    data = d.get("data") or {}
    songs = data.get("list") or data.get("songlist") or []
    if not songs:
        return None
    out = []
    disc = 1
    n = 1
    for s in songs:
        name = s2(s.get("songname") or s.get("songName") or s.get("name"))
        if not name:
            continue
        cd = int(s.get("cdIdx") or 1)
        if cd != disc:
            disc = cd
            n = 1
        iv = s.get("interval") or s.get("duration")
        try:
            dur = int(float(iv)) * 1000 if iv else None
        except Exception:
            dur = None
        out.append((disc, n, name, dur, "qq"))
        n += 1
    return out or None


# ---------------- 网易云 ----------------

def ne_find(album_name, artist):
    q = urllib.parse.quote(f"{album_name} {artist}")
    url = f"http://music.163.com/api/search/get/?s={q}&type=10&limit=10&offset=0"
    d = json_loads_or_none(http_get(url, headers=NE_H))
    if not d:
        return None
    for a in (d.get("result") or {}).get("albums") or []:
        ar = a.get("artist") or {}
        if album_match(album_name, a.get("name")) and artist_match(artist, ar.get("name")):
            return a.get("id")
    na = norm_album(album_name)
    for a in (d.get("result") or {}).get("albums") or []:
        if na and norm_album(a.get("name")) == na:
            return a.get("id")
    return None


def ne_tracks(aid):
    url = f"http://music.163.com/api/album/{aid}"
    d = json_loads_or_none(http_get(url, headers=NE_H))
    if not d or d.get("code") != 200:
        return None
    songs = (d.get("album") or {}).get("songs") or []
    if not songs:
        return None
    out = []
    counters = {}
    for s in songs:
        name = s2(s.get("name") or "")
        if not name:
            continue
        dn = int(s.get("disc") or 1)
        counters[dn] = counters.get(dn, 0) + 1
        tn = counters[dn]
        dur = s.get("duration")
        try:
            dur = int(dur) if dur else None
        except Exception:
            dur = None
        out.append((dn, tn, name, dur, "netease"))
    return out or None


# ---------------- main ----------------

def main():
    db = sqlite3.connect(DB)
    rows = db.execute("""
        SELECT a.album_id, a.album_name, a.artist, a.release_mbid, a.release_year
        FROM albums a
        WHERE a.status='active'
          AND NOT EXISTS (SELECT 1 FROM tracks t WHERE t.album_id = a.album_id)
        ORDER BY a.album_id
    """).fetchall()
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    if limit:
        rows = rows[:limit]
    print(f"待补: {len(rows)}")
    ok, fail = 0, 0
    log = []
    for aid, album, artist, mbid, year in rows:
        line = f"[{aid}] {artist} - {album}"
        tracks = None
        src = ""
        if mbid:
            tracks = mb_release_tracks_rate_limited(mbid)
            src = "mb-mbid"
        if not tracks and has_chinese(artist):
            cid = itunes_find(album, artist)
            if cid is None and not has_chinese(album):
                pass
            if cid:
                tracks = itunes_tracks(cid)
                src = "itunes"
            if not tracks:
                qaid = qq_find(album, artist)
                if qaid:
                    tracks = qq_tracks(qaid)
                    src = "qq"
                time.sleep(0.3)
        if not tracks and not has_chinese(artist):
            cid = itunes_find(album, artist)
            if cid:
                tracks = itunes_tracks(cid)
                src = "itunes"
            if not tracks:
                tracks = mb_search_tracks(album, artist)
                src = "mb-search"
        if not tracks:
            qaid = qq_find(album, artist)
            if qaid:
                tracks = qq_tracks(qaid)
                src = "qq"
            time.sleep(0.3)
        if not tracks:
            # last resort for non-chinese via MB search
            if not has_chinese(artist) and src != "mb-search":
                tracks = mb_search_tracks(album, artist)
                src = "mb-search"

        if tracks:
            db.execute("DELETE FROM tracks WHERE album_id=?", (aid,))
            db.executemany(
                "INSERT INTO tracks (album_id, track_number, track_name, duration, disc_number, source) VALUES (?,?,?,?,?,?)",
                [(aid, tn, s2(name), dur, dn, src) for dn, tn, name, dur, src in tracks])
            db.commit()
            cnt = len(tracks)
            ok += 1
            line += f" | OK {cnt} [{src}]"
            print(line, flush=True)
            log.append(f"{aid}\tOK\t{src}\t{cnt}\t{artist}\t{album}")
        else:
            fail += 1
            line += " | FAIL"
            print(line, flush=True)
            log.append(f"{aid}\tFAIL\t\t\t{artist}\t{album}")
        time.sleep(0.3)

    print(f"\n完成 {ok} OK / {fail} FAIL")
    with open(LOG, "w", encoding="utf-8") as f:
        f.write("\n".join(log) + "\n")
    db.close()


if __name__ == "__main__":
    main()