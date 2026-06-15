#!/usr/bin/env python3
"""Pitchfork Review Body Fetcher + Translator (fixed timeout).
Batch mode with per-URL timeout protection.
"""
import urllib.request, json, re, ssl, sys, os, time, threading

ctx = ssl._create_unverified_context()
sys.stdout.reconfigure(encoding="utf-8")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml",
}

# ── Helpers ─────────────────────────────────────────────────────

def fetch_html(url, timeout=15):
    """Fetch with timeout (urllib native timeout)."""
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        raise

def extract_preloaded_state(html):
    m = re.search(r'window\.__PRELOADED_STATE__\s*=\s*(\{.*?\})\s*;', html, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except:
        try:
            return json.loads(m.group(1) + "}")
        except:
            return None

def body_ir_to_markdown(ir, depth=0):
    if ir is None: return ""
    if isinstance(ir, str): return ir
    if isinstance(ir, list) and len(ir) > 0:
        tag = ir[0]
        children = ir[1:]
        if tag in ('native-ad', 'ad', 'inline-newsletter', 'inline-embed'):
            return ""
        if tag == 'p':
            return ''.join(body_ir_to_markdown(c, depth+1) for c in children) + '\n\n'
        elif tag in ('h2', 'h3', 'h4'):
            level = {'h2':2, 'h3':3, 'h4':4}[tag]
            text = ''.join(body_ir_to_markdown(c, depth+1) for c in children)
            return '#' * level + ' ' + text.strip() + '\n\n'
        elif tag == 'br': return '  \n'
        elif tag == 'hr': return '---\n\n'
        elif tag == 'blockquote':
            text = ''.join(body_ir_to_markdown(c, depth+1) for c in children)
            return '> ' + text.replace('\n', '\n> ') + '\n\n'
        elif tag == 'ul': return ''.join(body_ir_to_markdown(c, depth+1) for c in children) + '\n'
        elif tag == 'li':
            text = ''.join(body_ir_to_markdown(c, depth+1) for c in children)
            return '- ' + text.strip() + '\n'
        elif tag == 'em': return '*' + ''.join(body_ir_to_markdown(c, depth+1) for c in children) + '*'
        elif tag == 'strong': return '**' + ''.join(body_ir_to_markdown(c, depth+1) for c in children) + '**'
        elif tag == 'a':
            attrs = children[0] if children and isinstance(children[0], dict) else {}
            link_text = ''.join(body_ir_to_markdown(c, depth+1) for c in children[1:])
            href = attrs.get('href', '')
            return f'[{link_text}]({href})'
        elif tag == 'span':
            return ''.join(body_ir_to_markdown(c, depth+1) for c in children)
        else:
            return ''.join(body_ir_to_markdown(c, depth+1) for c in children)
    if isinstance(ir, dict): return ""
    return str(ir)

def get_review_body(url):
    try:
        html = fetch_html(url)
    except Exception as e:
        return None, f"Fetch failed: {e}"

    data = extract_preloaded_state(html)
    if not data:
        return None, "No __PRELOADED_STATE__ found"

    review = data.get("transformed", {}).get("review", {})
    header = review.get("headerProps", {})
    info = header.get("infoSliceFields", {})
    artist_list = header.get("artists", [{}])

    meta = {
        "url": url,
        "album": header.get("dangerousHed", "").replace("<em>", "").replace("</em>", ""),
        "artist": artist_list[0].get("name", "?") if artist_list else "?",
        "score": header.get("musicRating", {}).get("score"),
        "bnm": header.get("musicRating", {}).get("isBestNewMusic", False),
        "author": ", ".join(data.get("coreDataLayer", {}).get("content", {}).get("authorNames", [])),
        "date": info.get("reviewDate", ""),
        "label": info.get("label", ""),
        "year": info.get("releaseYear", ""),
    }

    body_ir = review.get("body", [])
    markdown = body_ir_to_markdown(body_ir).strip()
    return meta, markdown

def save_review(meta, markdown, out_dir="docs/en"):
    os.makedirs(out_dir, exist_ok=True)
    slug = meta["url"].rstrip("/").split("/")[-1]
    filename = os.path.join(out_dir, f"{slug}.md")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# {meta['artist']} — {meta['album']}\n\n")
        f.write(f"> Score: {meta['score']}  | BNM: {meta['bnm']}  | {meta['author']}  | {meta['date']}\n\n")
        f.write("---\n\n")
        f.write(markdown)
        f.write("\n")
    return filename

# ── Batch with per-URL timeout ────────────────────────────

def fetch_with_timeout(url, result, timeout=20):
    """Run get_review_body in a thread; set result on completion."""
    try:
        meta, body = get_review_body(url)
        result['meta'] = meta
        result['body'] = body
        result['done'] = True
    except Exception as e:
        result['error'] = str(e)
        result['done'] = True

def fetch_one(url, timeout=20):
    """Fetch one URL with thread-based timeout protection."""
    result = {'done': False}
    t = threading.Thread(target=fetch_with_timeout, args=(url, result, timeout))
    t.daemon = True
    t.start()
    t.join(timeout + 5)  # Wait up to timeout+5s

    if not result.get('done'):
        return None, f"TIMEOUT after {timeout}s"

    if result.get('error'):
        return None, result['error']

    return result.get('meta'), result.get('body')

# ── Main ─────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pf_review_body_v2.py <url_list.txt>")
        sys.exit(1)

    url_file = sys.argv[1]
    with open(url_file) as f:
        urls = [line.strip() for line in f if line.strip()]

    print(f"[PF Body v2] Batch: {len(urls)} URLs")
    for i, url in enumerate(urls, 1):
        print(f"  [{i}/{len(urls)}] {url[-50:]} ...", end="", flush=True)
        meta, body = fetch_one(url, timeout=20)
        if meta:
            fname = save_review(meta, body)
            print(f" OK (score={meta['score']}, {len(body)} chars)")
            print(f"    Saved: {fname}")
        else:
            print(f" FAIL: {body}")

    print("\n[PF Body v2] Done!")
