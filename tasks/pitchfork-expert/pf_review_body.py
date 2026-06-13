#!/usr/bin/env python3
"""Pitchfork Review Body Fetcher + Translator.
Fetches full review text from Pitchfork and saves as markdown.
Usage:
  python pf_review_body.py <review_url>
  python pf_review_body.py --file <url_list.txt>
  python pf_review_body.py --translate <review.md>
"""
import urllib.request, json, re, ssl, sys, os, time
sys.stdout.reconfigure(encoding="utf-8")

ctx = ssl._create_unverified_context()

# ── Body IR → Markdown converter ──────────────────────────────────────

def body_ir_to_markdown(ir, depth=0):
    if ir is None:
        return ""
    if isinstance(ir, str):
        return ir
    if isinstance(ir, list) and len(ir) > 0:
        tag = ir[0]
        children = ir[1:]
        # Skip ads/embeds
        if tag in ('native-ad', 'ad', 'inline-newsletter', 'inline-embed', 'product-card', 'one-cover', 'native-ad-unit'):
            return ""
        # Block elements
        if tag == 'p':
            text = ''.join(body_ir_to_markdown(c, depth+1) for c in children)
            return text + '\n\n'
        elif tag in ('h2', 'h3', 'h4'):
            level = {'h2':2, 'h3':3, 'h4':4}[tag]
            text = ''.join(body_ir_to_markdown(c, depth+1) for c in children)
            return '#' * level + ' ' + text.strip() + '\n\n'
        elif tag == 'cm-unit':
            return '***\n\n'
        elif tag == 'br':
            return '  \n'
        elif tag == 'hr':
            return '---\n\n'
        elif tag == 'blockquote':
            text = ''.join(body_ir_to_markdown(c, depth+1) for c in children)
            return '> ' + text.replace('\n', '\n> ') + '\n\n'
        elif tag == 'ul':
            text = ''.join(body_ir_to_markdown(c, depth+1) for c in children)
            return text + '\n'
        elif tag == 'li':
            text = ''.join(body_ir_to_markdown(c, depth+1) for c in children)
            return '- ' + text.strip() + '\n'
        # Inline elements
        elif tag == 'em':
            text = ''.join(body_ir_to_markdown(c, depth+1) for c in children)
            return '*' + text + '*'
        elif tag == 'strong':
            text = ''.join(body_ir_to_markdown(c, depth+1) for c in children)
            return '**' + text + '**'
        elif tag == 'a':
            attrs = children[0] if children and isinstance(children[0], dict) else {}
            link_text = ''.join(body_ir_to_markdown(c, depth+1) for c in children[1:])
            href = attrs.get('href', '')
            return f'[{link_text}]({href})'
        elif tag == 'span':
            return ''.join(body_ir_to_markdown(c, depth+1) for c in children)
        else:
            return ''.join(body_ir_to_markdown(c, depth+1) for c in children)
    if isinstance(ir, dict):
        return ""
    return str(ir)

# ── Fetch + extract ───────────────────────────────────────────────────

def fetch_html(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
        return resp.read().decode("utf-8", errors="replace")

def extract_preloaded_state(html):
    m = re.search(r'window\.__PRELOADED_STATE__\s*=\s*(\{.*?\})\s*;', html, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except:
            return None
    return None

def get_review_body(url):
    """Fetch review page and return (metadata_dict, markdown_body)."""
    html = fetch_html(url)
    data = extract_preloaded_state(html)
    if not data:
        return None, None
    
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
    """Save review as markdown file."""
    os.makedirs(out_dir, exist_ok=True)
    slug = meta["url"].rstrip("/").split("/")[-1]
    filename = os.path.join(out_dir, f"{slug}.md")
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# {meta['artist']} — {meta['album']}\n\n")
        f.write(f"> Score: {meta['score']}  ")
        f.write(f"| BNM: {meta['bnm']}  ")
        f.write(f"| {meta['author']}  ")
        f.write(f"| {meta['date']}\n\n")
        f.write("---\n\n")
        f.write(markdown)
        f.write("\n")
    
    print(f"[Saved] {filename}")
    return filename

# ── CLI ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pf_review_body.py <review_url> [--save]")
        print("       python pf_review_body.py --file <url_list.txt>")
        sys.exit(1)
    
    if sys.argv[1] == "--file":
        with open(sys.argv[2]) as f:
            urls = [line.strip() for line in f if line.strip()]
        print(f"[Pitchfork Body] Batch mode: {len(urls)} URLs")
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] {url}")
            try:
                meta, body = get_review_body(url)
                if meta:
                    save_review(meta, body)
                else:
                    print(f"  FAILED to extract")
            except Exception as e:
                print(f"  ERROR: {e}")
            time.sleep(1)
    else:
        url = sys.argv[1]
        print(f"[Pitchfork Body] {url}")
        meta, markdown = get_review_body(url)
        if meta:
            print(f"\n{'='*60}")
            print(f"  {meta['artist']} — {meta['album']}")
            print(f"  Score: {meta['score']} | BNM: {meta['bnm']} | {meta['author']}")
            print(f"{'='*60}\n")
            print(markdown[:500] + ("..." if len(markdown) > 500 else ""))
            print(f"\n[Total: {len(markdown)} chars]")
            if "--save" in sys.argv:
                save_review(meta, markdown)
        else:
            print("FAILED to extract review body")
