#!/usr/bin/env python3
"""
L项目歌词补齐管道 v3

v2 的两个正确性问题，这里修掉：

1. 网易云匹配不到曲名时会退回 `songs[0]['id']`，等于把别的歌的歌词写进来。
   v3 改为严格匹配，匹配不上就换源或放弃，绝不写错歌的歌词。
2. v2 的 `_lrc_from_plain()` 把纯文本原样写进 `.lrc` 文件，文件名带 .lrc 但
   里面一个时间标签都没有。下游按「有 lrc_path」判断能不能对时，会拿到
   一堆时间全为 0 的假时间轴。v3 只在真的有 `[mm:ss]` 标签时才写 .lrc。

匹配策略：先用剥掉 (Live)/(Demo)/副标题 后的干净曲名去搜，原始曲名只用于
落盘文件名——demo 版和录音室版在库里的曲名不同但歌词往往通用。
"""
import argparse
import json
import os
import random
import re
import socket
import sqlite3
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

DB = '/root/qclaw/tasks/2026-05-12-long-term-project/album-tracker/music'
ROOT = '/root/qclaw/tasks/lyrics-expert/lyrics'
LOG = '/root/qclaw/tasks/lyrics-expert/fetch_log.json'

UA = 'lyricsscroll-fetch/3.0 (album-tracker lyrics pipeline)'
WY_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
WY_HEADERS = {'User-Agent': WY_UA, 'Referer': 'https://music.163.com'}

LOCK = threading.Lock()
STATS = {'ok': 0, 'ok_plain': 0, 'miss': 0, 'instrumental': 0, 'error': 0}
SOURCES = {}

# 剥掉曲名里的噪音后缀，拿到真正的主歌名
NOISE = re.compile(
    r'\s*[\(\[][^\)\]]*?(live|demo|version|edit|remix|mix|mono|stereo|re-?master'
    r'|re-?record|instrumental|acoustic|demo \d|伴奏|现场|_demo)[^\)\]]*?[\)\]]',
    re.I)
TAIL_NOISE = re.compile(r'\s*[-–—]\s*(某|的)?.*?(片段|独奏|间奏|前奏|尾奏|演奏|纯音乐).*$')
ROMAN = re.compile(r'\s+[IVXL]{1,5}\s*$')
PART = re.compile(r'^(.*?)\s*(part|pt\.?)\s*\d+\s*$', re.I)

# 判定「这是纯音乐/无歌词」的标记，命中就当作不可用
INSTRUMENTAL = re.compile(
    r'^\s*(instrumental|instrumental version|纯音乐|纯器乐|器乐|无人声|'
    r'no lyrics|暂无歌词|无歌词|lyrics? not available)\s*$', re.I)


def has_cn(s):
    return bool(re.search(r'[\u4e00-\u9fff]', s or ''))


def safe(s):
    return re.sub(r'[\\/:*?"<>|\x00-\x1f]', '_', s)


def clean_name(name):
    """剥掉 demo/live/罗马数字等后缀，得到用于搜索的主歌名"""
    s = name or ''
    s = s.strip().strip('"\'“”')
    for _ in range(3):
        before = s
        s = NOISE.sub('', s)
        s = TAIL_NOISE.sub('', s)
        s = ROMAN.sub('', s)
        m = PART.match(s)
        if m and m.group(1):
            s = m.group(1)
        if s == before:
            break
    return s.strip().strip('-–— ').strip() or (name or '').strip()


def http_get(url, headers=None, timeout=12, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=headers or {'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode('utf-8', 'ignore')
        except urllib.error.HTTPError as e:
            if e.code in (404, 429, 403):
                return None
            if i == tries - 1:
                return None
            time.sleep(1.2 * (i + 1))
        except Exception:
            if i == tries - 1:
                return None
            time.sleep(1.0 * (i + 1))
    return None


def http_json(url, headers=None, timeout=12, tries=3):
    body = http_get(url, headers, timeout, tries)
    if not body:
        return None
    try:
        return json.loads(body)
    except ValueError:
        return None


def has_time_tag(lrc):
    """LRC 里至少要有一个 [mm:ss] 标签，否则不能算带时间轴"""
    return bool(re.search(r'\[(\d{1,3}):(\d{1,2})(?:[.:]\d{1,3})?\]', lrc or ''))


def lrc_to_plain(lrc):
    return '\n'.join(
        re.sub(r'^\[[^\]]*\]', '', ln).strip()
        for ln in (lrc or '').splitlines() if ln.strip()
    ).strip()


def judge(synced, plain):
    """返回 (状态, lrc, txt)；状态 ok / ok_plain / instrumental / miss

    instrumentAL：源明确标了纯音乐或没有歌词，属于「本来就没有」，不算缺口
    """
    txt = (plain or '').strip() or (lrc_to_plain(synced) if synced else '')
    if not txt:
        return 'miss', None, None
    if INSTRUMENTAL.match(txt) or len(txt.replace(' ', '')) < 12:
        return 'instrumental', None, None
    if synced and has_time_tag(synced):
        return 'ok', synced, txt
    return 'ok_plain', None, txt


# ---------------------------------------------------------------- LRCLIB

def from_lrclib(track, artist, album):
    """英文主源。返回 judge() 的三元组。artist/track 完全对不上就放弃。"""
    q = urllib.parse.quote('%s %s' % (artist, track))
    data = http_json('https://lrclib.net/api/search?q=' + q)
    if not isinstance(data, list):
        return 'miss', None, None
    t_low, a_low = track.lower(), (artist or '').lower()
    al_low = (album or '').lower()
    best = None
    for item in data:
        t_name = (item.get('trackName') or '').strip()
        a_name = (item.get('artistName') or '').strip()
        if not t_name:
            continue
        # 曲名要相等；艺人包含关系即可（库里的艺人名常带 [Hedgehog] 这类后缀）
        if t_name.lower() != t_low:
            continue
        if a_name.lower() != a_low and a_low not in a_name.lower() \
                and a_name.lower() not in a_low:
            continue
        synced = item.get('syncedLyrics') or ''
        plain = item.get('plainLyrics') or ''
        if not (synced or plain):
            continue
        score = 0
        if al_low and (item.get('albumName') or '').lower() == al_low:
            score = 2
        elif al_low and al_low in (item.get('albumName') or '').lower():
            score = 1
        if synced:
            score += 1
        if best is None or score > best[0]:
            best = (score, synced, plain)
    if best:
        return judge(best[1], best[2])
    return 'miss', None, None


# ---------------------------------------------------------------- 网易云

def from_netease(track, artist, album):
    """中文主源，同时是英文歌的兜底。严格按曲名匹配，不猜。"""
    for query in ('%s %s' % (track, artist), '%s %s' % (track, album or ''), track):
        if not query.strip():
            continue
        url = ('http://music.163.com/api/search/get?s=%s&type=1&limit=12'
               % urllib.parse.quote(query))
        data = http_json(url, WY_HEADERS)
        songs = (data or {}).get('result', {}).get('songs', [])
        if not songs:
            continue
        t_low = track.lower()
        # 库里曲名常带 [Live] 这类后缀，先按干净名找，再退到原名
        for cand in (clean_name(track).lower(), t_low):
            for s in songs:
                if (s.get('name') or '').strip().lower() != cand:
                    continue
                ld = http_json('http://music.163.com/api/song/lyric?id=%s&lv=1&tv=0'
                               % s['id'], WY_HEADERS)
                if not ld:
                    continue
                lrc = ((ld.get('lrc') or {}).get('lyric') or '')
                if not lrc:
                    continue
                state, lrc_out, txt = judge(lrc, None)
                if state != 'miss':
                    return state, lrc_out, txt
    return 'miss', None, None


# ---------------------------------------------------------------- 调度

def fetch_one(row):
    tid, name, artist, album = row
    cn = has_cn(artist) or has_cn(album) or has_cn(name)
    order = [('netease', from_netease), ('lrclib', from_lrclib)] if cn \
        else [('lrclib', from_lrclib), ('netease', from_netease)]
    clean = clean_name(name)
    for src_name, fn in order:
        for candidate in dict.fromkeys([clean, name.strip()]):
            try:
                state, lrc, txt = fn(candidate, artist, album)
            except Exception:
                state, lrc, txt = 'error', None, None
            if state in ('ok', 'ok_plain', 'instrumental'):
                with LOCK:
                    SOURCES[src_name] = SOURCES.get(src_name, 0) + 1
                return tid, state, lrc, txt, src_name
            time.sleep(0.35)
    return tid, 'miss', None, None, None


def load_missing(conn, mode):
    where = ("(t.lyrics_lrc_path IS NULL OR t.lyrics_lrc_path='') "
             "AND (t.lyrics_text_path IS NULL OR t.lyrics_text_path='')")
    if mode == 'lrc':
        # 只差时间轴：已有纯文本，只想补 LRC
        where = ("(t.lyrics_lrc_path IS NULL OR t.lyrics_lrc_path='') "
                 "AND (t.lyrics_text_path IS NOT NULL AND t.lyrics_text_path!='')")
    sql = ('SELECT t.id, t.track_name, a.artist, a.album_name '
           'FROM tracks t JOIN albums a ON a.album_id=t.album_id '
           'WHERE ' + where)
    if mode == 'lrc':
        sql += ' ORDER BY RANDOM()'
    return conn.execute(sql).fetchall()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['none', 'lrc', 'all'], default='none')
    ap.add_argument('--limit', type=int, default=0, help='0 = 不限')
    ap.add_argument('--probe', action='store_true', help='只统计命中率，不落盘')
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--random', action='store_true', help='随机取样，测真实命中率')
    ap.add_argument('--log', default=LOG)
    args = ap.parse_args()

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    rows = load_missing(conn, args.mode)
    if args.random and args.limit:
        random.shuffle(rows)
    if args.limit:
        rows = rows[:args.limit]
    if not rows:
        print('没有需要处理的曲目')
        return
    print('待处理 %d 首（mode=%s%s）' % (len(rows), args.mode, '，仅试跑' if args.probe else ''))

    t0 = time.time()
    done = 0
    log = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for res in pool.map(fetch_one, rows):
            tid, state, lrc, txt, src = res
            done += 1
            if args.probe:
                with LOCK:
                    STATS[state] = STATS.get(state, 0) + 1
                if done % 25 == 0 or done == len(rows):
                    el = time.time() - t0
                    rate = sum(v for k, v in STATS.items() if k in ('ok', 'ok_plain'))
                    print('  %d/%d  %5.0fs  命中 %d (%.0f%%)  纯音乐 %d  未命中 %d'
                          % (done, len(rows), el, rate, 100.0 * rate / done,
                             STATS.get('instrumental', 0), STATS.get('miss', 0)))
                continue
            if state in ('miss', 'error') or not txt:
                with LOCK:
                    STATS[state] = STATS.get(state, 0) + 1
                log.append({'id': tid, 'state': state})
                continue
            row = conn.execute(
                'SELECT t.track_number, t.album_id, a.artist, a.album_name '
                'FROM tracks t JOIN albums a ON a.album_id=t.album_id '
                'WHERE t.id=?', (tid,)).fetchone()
            if not row:
                continue
            album_dir = os.path.join(ROOT, safe(row['artist']), safe(row['album_name']))
            os.makedirs(album_dir, exist_ok=True)
            num = row['track_number'] or 0
            fname = ('%02d. %s' % (num, safe(row_album_track(tid, conn)))) if num \
                else safe(row_album_track(tid, conn))
            clash = conn.execute(
                'SELECT COUNT(*) FROM tracks WHERE album_id=? AND id!=? '
                "AND (lyrics_lrc_path LIKE ? OR lyrics_text_path LIKE ?)",
                (row['album_id'], tid, '%' + fname + '%', '%' + fname + '%')).fetchone()[0]
            if clash:
                fname = '%s [%d]' % (fname, tid)
            lrc_rel = txt_rel = None
            if lrc:
                with open(os.path.join(album_dir, fname + '.lrc'), 'w', encoding='utf-8') as f:
                    f.write(lrc)
                lrc_rel = os.path.relpath(os.path.join(album_dir, fname + '.lrc'), ROOT)
            with open(os.path.join(album_dir, fname + '.txt'), 'w', encoding='utf-8') as f:
                f.write(txt)
            txt_rel = os.path.relpath(os.path.join(album_dir, fname + '.txt'), ROOT)
            # 只补空的那一列，不覆盖已有的
            if lrc_rel:
                conn.execute('UPDATE tracks SET lyrics_lrc_path=COALESCE('
                             'NULLIF(lyrics_lrc_path,\'\'), ?) WHERE id=?', (lrc_rel, tid))
            conn.execute('UPDATE tracks SET lyrics_text_path=COALESCE('
                         'NULLIF(lyrics_text_path,\'\'), ?) WHERE id=?', (txt_rel, tid))
            conn.commit()
            with LOCK:
                STATS[state] = STATS.get(state, 0) + 1
                SOURCES[src] = SOURCES.get(src, 0) + 1
            log.append({'id': tid, 'state': state, 'src': src})
            if done % 20 == 0 or done == len(rows):
                el = time.time() - t0
                print('  %d/%d  %5.0fs  写入 LRC %d / 纯文本 %d  纯音乐 %d  未命中 %d'
                      % (done, len(rows), el, STATS.get('ok', 0),
                         STATS.get('ok_plain', 0), STATS.get('instrumental', 0),
                         STATS.get('miss', 0)), flush=True)

    print('\n完成：%d 首，耗时 %d 秒' % (len(rows), time.time() - t0))
    print('  带时间轴 %d  仅纯文本 %d  确认纯音乐/无词 %d  未命中 %d'
          % (STATS.get('ok', 0), STATS.get('ok_plain', 0),
             STATS.get('instrumental', 0), STATS.get('miss', 0)))
    print('  来源分布：%s' % (SOURCES or '（试跑未统计）'))
    if not args.probe:
        try:
            with open(args.log, 'w', encoding='utf-8') as f:
                json.dump(log, f, ensure_ascii=False)
            print('  日志：%s' % args.log)
        except Exception as e:
            print('  日志写入失败：%s' % e)


_NAME_CACHE = {}


def row_album_track(tid, conn):
    if tid not in _NAME_CACHE:
        _NAME_CACHE[tid] = conn.execute(
            'SELECT track_name FROM tracks WHERE id=?', (tid,)).fetchone()[0]
    return _NAME_CACHE[tid]


if __name__ == '__main__':
    main()
