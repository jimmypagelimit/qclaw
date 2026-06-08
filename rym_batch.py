import sys
import time
import json
import re
import os
from cloakbrowser import launch

sys.stdout.reconfigure(encoding='utf-8')

# Albums to fetch: (album_name, artist)
ALBUMS = [
    ("Disintegration", "The Cure"),
    ("Psychocandy", "The Jesus and Mary Chain"),
    ("Loveless", "My Bloody Valentine"),
    ("Daydream Nation", "Sonic Youth"),
    ("EVOL", "Sonic Youth"),
    ("Master of Reality", "Black Sabbath"),
    ("Dirt", "Alice In Chains"),
    ("Rubber Soul", "The Beatles"),
    ("Revolver", "The Beatles"),
    ("Please Please Me", "The Beatles"),
    ("Abbey Road", "The Beatles"),
    ("Plastic Ono Band", "John Lennon"),
    ("Ram", "Paul McCartney"),
    ("All Things Must Pass", "George Harrison"),
    ("Purple Rain", "Prince"),
    ("Presence", "Led Zeppelin"),
    ("The Piper at the Gates of Dawn", "Pink Floyd"),
    ("The Dark Side of the Moon", "Pink Floyd"),
    ("Close to the Edge", "Yes"),
    ("Synchronicity", "The Police"),
    ("Heaven or Las Vegas", "Cocteau Twins"),
    ("Crooked Rain, Crooked Rain", "Pavement"),
    ("Life's Rich Pageant", "R.E.M."),
    ("American Idiot", "Green Day"),
    ("In Rainbows", "Radiohead"),
    ("Arrival", "ABBA"),
    ("The Visitors", "ABBA"),
    ("Monomania", "Car Seat Headrest"),
    ("Teens of Denial", "Car Seat Headrest"),
    ("Twin Fantasy", "Car Seat Headrest"),
    ("Capacity", "Big Thief"),
    ("Dragon New Warm Mountain I Believe in You", "Big Thief"),
    ("On Avery Island", "Neutral Milk Hotel"),
    ("Wintersun", "Wintersun"),
    ("New Bermuda", "Deafheaven"),
    ("Sunbather", "Deafheaven"),
    ("The Jester Race", "In Flames"),
    ("Megadeth", "Megadeth"),
    ("Symbolic", "Death"),
    ("Kiss Me Kiss Me Kiss Me", "The Cure"),
    ("The Head on the Door", "The Cure"),
    ("Pornography", "The Cure"),
    ("Wild Mood Swings", "The Cure"),
    ("The Cure", "The Cure"),
    ("Misery Is a Butterfly", "Blonde Redhead"),
    ("Wall of Eyes", "The Smile"),
    ("Crimson", "Edge of Sanity"),
    ("De mysteriis Dom Sathanas", "Mayhem"),
    ("Hasta la raiz", "Natalia Lafourcade"),
    ("Cancionera", "Natalia Lafourcade"),
    ("Soldatenschicksale", "Kanonenfieber"),
    ("Red", "King Crimson"),
    ("In the Court of the Crimson King", "King Crimson"),
    ("Breakfast in America", "Supertramp"),
    ("Famous Last Words", "Supertramp"),
    ("Hunky Dory", "David Bowie"),
    ("Savior", "Green Day"),
    ("Creature of Habit", "Courtney Barnett"),
    ("American Football", "American Football"),
    ("Secret love", "Dry Cleaning"),
    ("Loney People With Power", "deafHeaven"),
    ("Middle of Nowhere", "Kacey Musgraves"),
    ("Train on the Island", "Aldous Harding"),
    ("The Mountain", "Gorillaz"),
    ("Marathon", "Maria BC"),
    ("Angel in Plainclothes", "Angelo De Augustine"),
    ("Hell for a Basement", "drug bug"),
    ("U", "underscores"),
    ("Girlfriend", "Grace Ives"),
    ("Nothing's About to Happen to Me", "Mitski"),
    ("Death in the Business of Whaling", "Searows"),
    ("Post Recovery", "midwest post death"),
    ("Necropalace", "Worm"),
    ("An Undying Love for a Burning World", "Neurosis"),
    ("It's the Long Goodbye", "The Twilight Sad"),
    ("Blood At Ease", "Blood At Ease"),
    ("Days of Ash", "U2"),
    ("Under Cover", "Ozzy Osbourne"),
    ("Living's Deal", "Explosicum"),
    ("Almighty So 2", "Chief Keef"),
    ("That! Feel! Good!", "Jessie Ware"),
    ("The Apple Tree Under the Sea", "Hemlocke Springs"),
    ("Blame the Clown", "Twisted Teens"),
    ("Overspace & Supertime", "Cryptic Shift"),
    ("Setting Fire to the Sky", "Urne"),
    ("Peanut", "Otto Benson"),
    ("Some Things Never Leave", "Annabelle Dinda"),
    ("An Evergreen Joke", "Snorkmaiden"),
    ("Singin' to an Empty Chair", "Ratboys"),
    ("The Sound of One Car Crashing", "threadbaron"),
    ("No ritmo da Terra", "Antropoceno"),
    ("tanquemante", "Inundaremos"),
    ("Everything", "Black Sea Dahu"),
    ("Picture Day", "The Fencesitters"),
    ("Help", "Various Artists War Child Records"),
    ("El hambre y las ganas de comer", "La Estrategia del Caracol"),
    ("Something Worth Waiting For", "Friko"),
    ("You Are in My Dreams", "Kisses"),
    ("It's Fine to Dream", "You Are an Angel"),
    ("American Road in New Jersey", "American Road In New Jersey"),
    ("Jessica Pratt", "Asher White"),
    ("Itinerary", "Jo's Moving Day"),
    ("Casino", "Richard Sallis"),
    ("Repetition", "Kill-Kennie"),
    ("Cainite", "The Mensis Ritual"),
    ("Is It Gonna Happen Again?", "jody"),
    ("Is It Gonna Happen Again?", "jody"),
]

OUTPUT_FILE = r'C:\Users\qujt\.qclaw\workspace\rym_batch_results.json'

def search_and_extract(page, album_name, artist_name):
    query = "%s %s" % (album_name, artist_name)
    
    try:
        # Search
        search_box = page.locator("#ui_search_input_main_search").first
        search_box.click()
        time.sleep(0.5)
        search_box.fill("")
        time.sleep(0.3)
        search_box.type(query, delay=60)
        time.sleep(0.5)
        search_box.press("Enter")
        time.sleep(12)
        
        # Click first album
        js = """() => {
            const links = document.querySelectorAll('a[href*="/release/"]');
            if (links.length > 0) { links[0].click(); return true; }
            return false;
        }"""
        page.evaluate(js)
        time.sleep(15)
        
        # Extract
        html = page.content()
        info = {'album_name': album_name, 'artist_name': artist_name}
        
        m = re.search(r'<title>(.*?)\s+by\s+', html, re.DOTALL)
        if m: info['rym_title'] = m.group(1).strip()
        
        m = re.search(r'class="artist"[^>]*>(.*?)</(?:a|span)', html, re.DOTALL)
        if m:
            a = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            if a: info['rym_artist'] = a
        
        m = re.search(r'class="avg_rating"[^>]*>(.*?)</', html, re.DOTALL)
        if m:
            r = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            if r: info['rym_rating'] = r
        
        m = re.search(r'class="num_ratings"[^>]*>(.*?)</', html, re.DOTALL)
        if m:
            r = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            m2 = re.search(r'([\d,]+)', r)
            if m2: info['rym_num_ratings'] = m2.group(1)
        
        m = re.search(r'([\d,]+)\s*Reviews?', html)
        if m: info['rym_num_reviews'] = m.group(1)
        
        # Release year
        m = re.search(r'release_year[^>]*><a[^>]*>(\d{4})</a>', html)
        if m: info['rym_release_year'] = m.group(1)
        
        # Country
        m = re.search(r'item_country[^>]*><a[^>]*>([^<]+)</a>', html)
        if m: info['rym_country'] = m.group(1).strip()
        
        # Genres
        genres = re.findall(r'href="/genre/([^"/]+)', html)
        if genres:
            seen = set()
            unique = []
            for g in genres:
                g = g.replace("-", " ")
                if g not in seen:
                    seen.add(g)
                    unique.append(g)
            info['rym_genres'] = unique[:8]
        
        # Styles
        styles = re.findall(r'href="/style/([^"/]+)', html)
        if styles:
            seen = set()
            unique = []
            for s in styles:
                s = s.replace("-", " ")
                if s not in seen:
                    seen.add(s)
                    unique.append(s)
            info['rym_styles'] = unique[:8]
        
        return info
        
    except Exception as e:
        return {'album_name': album_name, 'artist_name': artist_name, 'error': str(e)}


def main():
    print("=== RYM Batch Fetcher ===")
    print("Total albums: %d" % len(ALBUMS))
    print("Estimated time: %d min" % (len(ALBUMS) * 50 // 60))
    print()
    
    results = []
    failed = []
    
    browser = launch(headless=False)
    page = browser.new_page()
    
    print("[0] Loading RYM homepage (20s for CF)...")
    page.goto("https://rateyourmusic.com/", timeout=90000)
    time.sleep(20)
    print("    CF OK")
    
    for i, (album, artist) in enumerate(ALBUMS):
        print("\n[%d/%d] %s - %s" % (i+1, len(ALBUMS), artist, album))
        info = search_and_extract(page, album, artist)
        results.append(info)
        
        if 'error' in info:
            failed.append("%s - %s: %s" % (artist, album, info['error']))
            print("    ERROR: %s" % info['error'])
        else:
            rating = info.get('rym_rating', 'N/A')
            genres = info.get('rym_genres', [])
            styles = info.get('rym_styles', [])
            print("    Rating: %s/5 | Genres: %s" % (rating, ', '.join(genres[:3]) if genres else 'N/A'))
        
        # Go back to homepage for next search
        try:
            page.goto("https://rateyourmusic.com/", timeout=30000)
            time.sleep(3)
        except:
            time.sleep(5)
    
    browser.close()
    
    # Save results
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("\n=== DONE ===")
    print("Saved: %s" % OUTPUT_FILE)
    print("Success: %d / %d" % (len(results) - len(failed), len(ALBUMS)))
    if failed:
        print("\nFailed:")
        for f in failed:
            print("  - %s" % f)

if __name__ == "__main__":
    main()
