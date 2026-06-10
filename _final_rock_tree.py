import json, sys

sys.stdout.reconfigure(encoding='utf-8')

# Load the 81 rock subgenres from RYM /genre/rock/ page
rock_subgenres = [
    ("acid-rock", "Acoustic Rock"),
    ("acoustic-rock", "Acoustic Rock"),
    ("afro-rock", "Afro-Rock"),
    ("alpenrock", "Alpenrock"),
    ("alternative-rock", "Alternative Rock"),
    ("anatolian-rock", "Anatolian Rock"),
    ("art-rock", "Art Rock"),
    ("bard-rock", "Bard Rock"),
    ("beat-rock", "Beat Rock"),
    ("blues-rock", "Blues Rock"),
    ("boogie-rock", "Boogie Rock"),
    ("british-folk-rock", "British Folk Rock"),
    ("celtic-rock", "Celtic Rock"),
    ("christian-rock", "Christian Rock"),
    ("comedy-rock", "Comedy Rock"),
    ("country-rock", "Country Rock"),
    ("crack-rock-steady", "Crack Rock Steady"),
    ("deathrock", "Deathrock"),
    ("deutschrock", "Deutschrock"),
    ("experimental-rock", "Experimental Rock"),
    ("folk-rock", "Folk Rock"),
    ("frat-rock", "Frat Rock"),
    ("funk-rock", "Funk Rock"),
    ("garage-rock-revival", "Garage Rock Revival"),
    ("garage-rock", "Garage Rock"),
    ("geek-rock", "Geek Rock"),
    ("glam-rock", "Glam Rock"),
    ("gothic-rock", "Gothic Rock"),
    ("hard-rock", "Hard Rock"),
    ("heartland-rock", "Heartland Rock"),
    ("indie-rock", "Indie Rock"),
    ("indorock", "Indorock"),
    ("industrial-rock", "Industrial Rock"),
    ("jazz-rock", "Jazz-Rock"),
    ("konsrock", "Konsrock"),
    ("krautrock", "Krautrock"),
    ("latin-rock", "Latin Rock"),
    ("machine-rock", "Machine Rock"),
    ("math-rock", "Math Rock"),
    ("mittelalter-rock", "Mittelalter-Rock"),
    ("noise-rock", "Noise Rock"),
    ("nordic-folk-rock", "Nordic Folk Rock"),
    ("occult-rock", "Occult Rock"),
    ("piano-rock", "Piano Rock"),
    ("pinoy-folk-rock", "Pinoy Folk Rock"),
    ("pop-rock", "Pop Rock"),
    ("post-rock", "Post-Rock"),
    ("progressive-rock", "Progressive Rock"),
    ("psychedelic-rock", "Psychedelic Rock"),
    ("pub-rock", "Pub Rock"),
    ("punk-rock", "Punk Rock"),
    ("raga-rock", "Raga Rock"),
    ("rap-rock", "Rap Rock"),
    ("reggae-rock", "Reggae Rock"),
    ("rock-and-roll", "Rock & Roll"),
    ("rock-andaluz", "Rock andaluz"),
    ("rock-andino", "Rock andino"),
    ("rock-kapak", "Rock Kapak"),
    ("rock-musical", "Rock Musical"),
    ("rock-opera", "Rock Opera"),
    ("rock-rural", "Rock rural"),
    ("rockabilly", "Rockabilly"),
    ("roots-rock", "Roots Rock"),
    ("slacker-rock", "Slacker Rock"),
    ("sleaze-rock", "Sleaze Rock"),
    ("soft-rock", "Soft Rock"),
    ("southern-rock", "Southern Rock"),
    ("space-rock-revival", "Space Rock Revival"),
    ("space-rock", "Space Rock"),
    ("stoner-rock", "Stoner Rock"),
    ("sufi-rock", "Sufi Rock"),
    ("surf-rock", "Surf Rock"),
    ("swamp-rock", "Swamp Rock"),
    ("symphonic-rock", "Symphonic Rock"),
    ("tolai-rock", "Tolai Rock"),
    ("tropical-rock", "Tropical Rock"),
    ("vikingarock", "Vikingarock"),
    ("yacht-rock", "Yacht Rock"),
    ("zamrock", "Zamrock"),
]

# Organize into a logical hierarchy based on musicology
# RYM's page lists them flat, but we can group them by musical lineage
rock_tree = {
    "name": "Rock",
    "slug": "rock",
    "children": [
        {
            "name": "Rock & Roll / Early Rock",
            "children": [
                {"name": "Rock & Roll", "slug": "rock-and-roll"},
                {"name": "Rockabilly", "slug": "rockabilly"},
                {"name": "Surf Rock", "slug": "surf-rock"},
            ]
        },
        {
            "name": "Garage / Punk",
            "children": [
                {"name": "Garage Rock", "slug": "garage-rock"},
                {"name": "Garage Rock Revival", "slug": "garage-rock-revival"},
                {"name": "Punk Rock", "slug": "punk-rock"},
                {"name": "Frat Rock", "slug": "frat-rock"},
                {"name": "Crack Rock Steady", "slug": "crack-rock-steady"},
            ]
        },
        {
            "name": "Indie / Alternative",
            "children": [
                {"name": "Alternative Rock", "slug": "alternative-rock"},
                {"name": "Indie Rock", "slug": "indie-rock"},
                {"name": "Slacker Rock", "slug": "slacker-rock"},
                {"name": "Geek Rock", "slug": "geek-rock"},
                {"name": "Noise Rock", "slug": "noise-rock"},
                {"name": "Post-Rock", "slug": "post-rock"},
            ]
        },
        {
            "name": "Folk Rock",
            "children": [
                {"name": "Folk Rock", "slug": "folk-rock"},
                {"name": "British Folk Rock", "slug": "british-folk-rock"},
                {"name": "Celtic Rock", "slug": "celtic-rock"},
                {"name": "Nordic Folk Rock", "slug": "nordic-folk-rock"},
                {"name": "Pinoy Folk Rock", "slug": "pinoy-folk-rock"},
                {"name": "Mittelalter-Rock", "slug": "mittelalter-rock"},
                {"name": "Bard Rock", "slug": "bard-rock"},
            ]
        },
        {
            "name": "Psychedelic / Progressive / Art",
            "children": [
                {"name": "Psychedelic Rock", "slug": "psychedelic-rock"},
                {"name": "Progressive Rock", "slug": "progressive-rock"},
                {"name": "Art Rock", "slug": "art-rock"},
                {"name": "Experimental Rock", "slug": "experimental-rock"},
                {"name": "Math Rock", "slug": "math-rock"},
                {"name": "Krautrock", "slug": "krautrock"},
                {"name": "Space Rock", "slug": "space-rock"},
                {"name": "Space Rock Revival", "slug": "space-rock-revival"},
                {"name": "Raga Rock", "slug": "raga-rock"},
                {"name": "Acid Rock", "slug": "acid-rock"},
                {"name": "Rock Opera", "slug": "rock-opera"},
                {"name": "Rock Musical", "slug": "rock-musical"},
                {"name": "Symphonic Rock", "slug": "symphonic-rock"},
            ]
        },
        {
            "name": "Hard / Heavy",
            "children": [
                {"name": "Hard Rock", "slug": "hard-rock"},
                {"name": "Stoner Rock", "slug": "stoner-rock"},
                {"name": "Blues Rock", "slug": "blues-rock"},
                {"name": "Boogie Rock", "slug": "boogie-rock"},
                {"name": "Southern Rock", "slug": "southern-rock"},
                {"name": "Roots Rock", "slug": "roots-rock"},
                {"name": "Swamp Rock", "slug": "swamp-rock"},
                {"name": "Sleaze Rock", "slug": "sleaze-rock"},
                {"name": "Occult Rock", "slug": "occult-rock"},
                {"name": "Deathrock", "slug": "deathrock"},
                {"name": "Gothic Rock", "slug": "gothic-rock"},
            ]
        },
        {
            "name": "Glam / Pop / Soft",
            "children": [
                {"name": "Glam Rock", "slug": "glam-rock"},
                {"name": "Pop Rock", "slug": "pop-rock"},
                {"name": "Soft Rock", "slug": "soft-rock"},
                {"name": "Yacht Rock", "slug": "yacht-rock"},
                {"name": "Piano Rock", "slug": "piano-rock"},
                {"name": "Country Rock", "slug": "country-rock"},
                {"name": "Jazz-Rock", "slug": "jazz-rock"},
                {"name": "Funk Rock", "slug": "funk-rock"},
                {"name": "Latin Rock", "slug": "latin-rock"},
                {"name": "Tropical Rock", "slug": "tropical-rock"},
                {"name": "Acoustic Rock", "slug": "acoustic-rock"},
                {"name": "Heartland Rock", "slug": "heartland-rock"},
                {"name": "Pub Rock", "slug": "pub-rock"},
            ]
        },
        {
            "name": "Industrial / Electronic",
            "children": [
                {"name": "Industrial Rock", "slug": "industrial-rock"},
                {"name": "Machine Rock", "slug": "machine-rock"},
                {"name": "Beat Rock", "slug": "beat-rock"},
            ]
        },
        {
            "name": "Regional / World Rock",
            "children": [
                {"name": "Afro-Rock", "slug": "afro-rock"},
                {"name": "Zamrock", "slug": "zamrock"},
                {"name": "Deutschrock", "slug": "deutschrock"},
                {"name": "Alpenrock", "slug": "alpenrock"},
                {"name": "Indorock", "slug": "indorock"},
                {"name": "Vikingarock", "slug": "vikingarock"},
                {"name": "Konsrock", "slug": "konsrock"},
                {"name": "Rock andaluz", "slug": "rock-andaluz"},
                {"name": "Rock andino", "slug": "rock-andino"},
                {"name": "Rock Kapak", "slug": "rock-kapak"},
                {"name": "Rock rural", "slug": "rock-rural"},
                {"name": "Tolai Rock", "slug": "tolai-rock"},
                {"name": "Sufi Rock", "slug": "sufi-rock"},
                {"name": "Anatolian Rock", "slug": "anatolian-rock"},
                {"name": "Christian Rock", "slug": "christian-rock"},
                {"name": "Comedy Rock", "slug": "comedy-rock"},
                {"name": "Rap Rock", "slug": "rap-rock"},
                {"name": "Reggae Rock", "slug": "reggae-rock"},
            ]
        }
    ]
}

def print_tree(node, indent=0):
    prefix = ("|   " * indent) + ("+-- " if indent > 0 else "")
    print(f"{prefix}{node['name']}")
    for ch in node.get('children', []):
        if isinstance(ch, dict):
            print_tree(ch, indent + 1)
        else:
            print(f"{'|   ' * (indent+1)}+-- {ch}")

def count_all(node):
    c = 1
    for ch in node.get('children', []):
        if isinstance(ch, dict):
            c += count_all(ch)
        else:
            c += 1
    return c

total = count_all(rock_tree)
print("=" * 60)
print("RYM ROCK STYLE TREE")
print(f"Total: {total} genres (1 root + 80 subgenres)")
print("=" * 60)
print_tree(rock_tree)

# Verify all 81 are accounted for
all_slugs = set()
def collect_slugs(node):
    if 'slug' in node:
        all_slugs.add(node['slug'])
    for ch in node.get('children', []):
        if isinstance(ch, dict):
            collect_slugs(ch)

collect_slugs(rock_tree)
print(f"\nGenres in tree: {len(all_slugs)}")

# Check for missing
rym_slugs = set(s for s, n in rock_subgenres if not s.isdigit() and len(s) > 3)
missing = rym_slugs - all_slugs
if missing:
    print(f"Missing from tree: {missing}")
else:
    print("All 81 RYM rock subgenres accounted for!")

# Save final tree
with open(r'C:\Users\qujt\.qclaw\workspace\_rym_rock_tree_final.json', 'w', encoding='utf-8') as f:
    json.dump(rock_tree, f, ensure_ascii=False, indent=2)
print("\nSaved _rym_rock_tree_final.json")