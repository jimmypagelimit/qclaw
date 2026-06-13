"""Extract body from saved HTML, then save."""
import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")

with open(r"C:\Users\qujt\.qclaw\workspace\tasks\pitchfork-expert\_tod_raw.html", encoding="utf-8") as f:
    html = f.read()

def body_ir_to_markdown(ir, depth=0):
    if ir is None: return ""
    if isinstance(ir, str): return ir
    if isinstance(ir, list) and len(ir) > 0:
        tag = ir[0]; children = ir[1:]
        if tag in ('native-ad', 'ad', 'inline-newsletter', 'inline-embed', 'product-card', 'one-cover', 'native-ad-unit'): return ""
        if tag == 'p':
            text = ''.join(body_ir_to_markdown(c, depth+1) for c in children)
            return text + '\n\n'
        elif tag in ('h2','h3','h4'):
            level = {'h2':2,'h3':3,'h4':4}[tag]
            text = ''.join(body_ir_to_markdown(c, depth+1) for c in children)
            return '#'*level + ' ' + text.strip() + '\n\n'
        elif tag == 'cm-unit': return '***\n\n'
        elif tag == 'br': return '  \n'
        elif tag == 'hr': return '---\n\n'
        elif tag == 'blockquote':
            text = ''.join(body_ir_to_markdown(c, depth+1) for c in children)
            return '> ' + text.replace('\n', '\n> ') + '\n\n'
        elif tag == 'ul': return ''.join(body_ir_to_markdown(c, depth+1) for c in children) + '\n'
        elif tag == 'li':
            text = ''.join(body_ir_to_markdown(c, depth+1) for c in children)
            return '- ' + text.strip() + '\n'
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
        elif tag == 'span': return ''.join(body_ir_to_markdown(c, depth+1) for c in children)
        else: return ''.join(body_ir_to_markdown(c, depth+1) for c in children)
    if isinstance(ir, dict): return ""
    return str(ir)

m = re.search(r'window\.__PRELOADED_STATE__\s*=\s*(\{.*?\})\s*;', html, re.DOTALL)
data = json.loads(m.group(1))
body_ir = data['transformed']['review']['body']
markdown = body_ir_to_markdown(body_ir).strip()

print(f"Body: {len(markdown)} chars, ~{len(markdown.split())} words")
print("\n" + markdown[:200] + ("..." if len(markdown) > 200 else ""))

# Save English
en_path = r"C:\Users\qujt\.qclaw\workspace\tasks\pitchfork-expert\docs\en\car-seat-headrest-teens-of-denial.md"
with open(en_path, "w", encoding="utf-8") as f:
    f.write(f"# Car Seat Headrest — Teens of Denial\n\n")
    f.write(f"> Score: 8.5 | BNM: True | Author:  | May 20, 2016\n")
    f.write(f"> URL: https://pitchfork.com/reviews/albums/21673-teens-of-denial/\n\n")
    f.write("---\n\n")
    f.write(markdown + "\n")
print(f"\n[Saved EN] {en_path}")
