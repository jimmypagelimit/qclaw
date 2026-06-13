#!/usr/bin/env python3
"""Convert Pitchfork review['body'] (list IR) to Markdown text."""
import urllib.request, json, re, ssl, sys
sys.stdout.reconfigure(encoding="utf-8")

ctx = ssl._create_unverified_context()

def fetch_html(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
        return resp.read().decode("utf-8", errors="replace")

def body_ir_to_markdown(ir, depth=0):
    """Convert Pitchfork body IR (nested list) to Markdown text.
    
    IR format observed:
    - ['p', 'text', ['em', 'italic'], ...]  -> paragraph
    - ['h2', ...]                                 -> heading
    - ['a', {'href':...}, 'text']                -> link
    - ['em', ...]                                -> italic
    - ['strong', ...]                            -> bold
    - ['cm-unit']                                -> *** separator
    - ['inline-newsletter']                      -> skip
    - ['native-ad', ...]                         -> skip
    - ['ad', ...]                               -> skip
    """
    if ir is None:
        return ""
    
    # String leaf node
    if isinstance(ir, str):
        return ir
    
    # List node: [tag, ...children]
    if isinstance(ir, list) and len(ir) > 0:
        tag = ir[0]
        children = ir[1:]
        
        # Skip ads/embeds
        if tag in ('native-ad', 'ad', 'inline-newsletter', 'inline-embed', 'product-card', 'one-cover'):
            return ""
        
        # Block elements
        if tag == 'p':
            text = ''.join(body_ir_to_markdown(c, depth+1) for c in children)
            return text + '\n\n'
        elif tag == 'h2':
            text = ''.join(body_ir_to_markdown(c, depth+1) for c in children)
            return '## ' + text + '\n\n'
        elif tag == 'h3':
            text = ''.join(body_ir_to_markdown(c, depth+1) for c in children)
            return '### ' + text + '\n\n'
        elif tag == 'cm-unit':
            return '***\n\n'
        elif tag == 'br':
            return '  \n'
        elif tag == 'hr':
            return '---\n\n'
        
        # Inline elements
        elif tag == 'em':
            text = ''.join(body_ir_to_markdown(c, depth+1) for c in children)
            return '*' + text + '*'
        elif tag == 'strong':
            text = ''.join(body_ir_to_markdown(c, depth+1) for c in children)
            return '**' + text + '**'
        elif tag == 'a':
            # ['a', {'href':..., 'isExternal':...}, 'text']
            attrs = children[0] if children and isinstance(children[0], dict) else {}
            link_text = ''.join(body_ir_to_markdown(c, depth+1) for c in children[1:])
            href = attrs.get('href', '')
            return f'[{link_text}]({href})'
        
        # Default: recurse into children
        else:
            return ''.join(body_ir_to_markdown(c, depth+1) for c in children)
    
    # Dict node (attrs only, no content)
    if isinstance(ir, dict):
        return ""
    
    return str(ir)

# Fetch and extract
url = "https://pitchfork.com/reviews/albums/car-seat-headrest-twin-fantasy/"
html = fetch_html(url)
m = re.search(r'window\.__PRELOADED_STATE__\s*=\s*(\{.*?\})\s*;', html, re.DOTALL)
data = json.loads(m.group(1))
body_ir = data['transformed']['review']['body']

print(f"Body IR type: {type(body_ir)}, len: {len(body_ir) if isinstance(body_ir, list) else 'N/A'}")
print("\n=== Markdown Output ===\n")
markdown = body_ir_to_markdown(body_ir)
print(markdown)
print(f"\n=== Stats ===")
print(f"Total chars: {len(markdown)}")
print(f"Words (approx): {len(markdown.split())}")
