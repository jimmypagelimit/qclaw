import sys, time, re, json

sys.stdout.reconfigure(encoding='utf-8')
from cloakbrowser import launch

print("=== RYM Rock Full Hierarchy ===")
browser = launch(headless=False)
page = browser.new_page()

# CF
print("[1/5] Main page (CF)...")
page.goto("https://rateyourmusic.com/", timeout=90000)
time.sleep(30)
for i in range(5):
    try:
        t = page.evaluate("document.title")
        if '请稍候' not in str(t): break
    except: pass
    time.sleep(3)

# Navigate to /genre/rock/
print("[2/5] Navigate to /genre/rock/")
page.evaluate("() => { window.location.href = '/genre/rock/'; }")
time.sleep(25)

title = page.evaluate("document.title")
print(f"  Title: {repr(title)}")

# Click "Expand Hierarchy" button
print("[3/5] Expanding hierarchy...")
try:
    # Try multiple selectors for the expand button
    expand_selectors = [
        'text="Expand Hierarchy"',
        'text="expand hierarchy"',
        'text="Expand"',
        '[class*="expand"]',
        'button:has-text("Expand")',
        'a:has-text("Expand")',
    ]
    
    clicked = False
    for sel in expand_selectors:
        try:
            page.click(sel, timeout=3000)
            print(f"  Clicked: {sel}")
            clicked = True
            break
        except:
            pass
    
    if not clicked:
        # JS fallback - find and click any expand button
        page.evaluate("""() => {
            const buttons = document.querySelectorAll('button, a, [role="button"]');
            for (const b of buttons) {
                const text = b.textContent.trim().toLowerCase();
                if (text.includes('expand') || text.includes('hierarchy')) {
                    b.click();
                    return 'Clicked: ' + b.textContent.trim();
                }
            }
            return 'No expand button found';
        }""")
    
    time.sleep(10)  # Wait for expansion
    
except Exception as e:
    print(f"  Expand error: {str(e)[:60]}")

# Also try clicking individual genre items that might have children
print("[4/5] Expanding sub-items...")
# Click items with children indicators (arrows, + signs, etc.)
page.evaluate("""() => {
    // Find all clickable elements in the hierarchy section
    const hierarchySection = document.querySelector('[class*="hierarchy"]') || 
                             document.querySelector('#hierarchy');
    if (!hierarchySection) return 'No hierarchy section found';
    
    // Find all expandable items (usually have a class like 'expandable' or 'has-children')
    let count = 0;
    const items = hierarchySection.querySelectorAll('[class*="expand"], [class*="toggle"], [aria-expanded]');
    items.forEach(item => {
        if (item.getAttribute('aria-expanded') === 'false') {
            item.click();
            count++;
        }
    });
    
    // Also try clicking on genre names that look like they have children
    const links = hierarchySection.querySelectorAll('a[href*="/genre/"]');
    links.forEach(link => {
        const parent = link.closest('[class*="item"], [class*="row"], li');
        if (parent && (parent.className.includes('parent') || parent.className.includes('has-child'))) {
            link.click();
            count++;
        }
    });
    
    return 'Expanded ' + count + ' items';
}""")

time.sleep(5)

# Extract final state
print("[5/5] Extracting full hierarchy...")
html = page.content()
page.screenshot(path=r'C:\Users\qujt\.qclaw\workspace\_rym_rock_hierarchy.png', full_page=True)

with open(r'C:\Users\qujt\.qclaw\workspace\_rym_rock_hierarchy.html', 'w', encoding='utf-8') as f:
    f.write(html)

# Count rock genre links
links = re.findall(r'href="/genre/([^"]+)"[^>]*>([^<]+)</a>', html)
rock_links = [(u, n.strip()) for u, n in links if 'rock' in u.lower()]
unique_rock = sorted(set(rock_links), key=lambda x: x[0])

print(f"\nTotal links: {len(links)}")
print(f"Rock-related: {len(unique_rock)}")

for slug, name in unique_rock:
    print(f"  /{slug}/ -> {name}")

print("\nDone!")
browser.close()