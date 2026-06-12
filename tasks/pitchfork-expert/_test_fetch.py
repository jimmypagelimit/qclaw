"""
Pitchfork Expert - 专辑评论抓取脚本
"""
import sys, os, json, re, time, argparse
from cloakbrowser import launch

sys.stdout.reconfigure(encoding="utf-8")

OUTPUT_DIR = r"C:\Users\qujt\.qclaw\workspace\tasks\pitchfork-expert\data"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def parse_album_list(html_text):
    """解析 Pitchfork 专辑列表页"""
    reviews = []
    
    # JSON-LD ItemList
    jsonld_blocks = re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', html_text, re.DOTALL
    )
    for block in jsonld_blocks:
        try:
            data = json.loads(block)
            if data.get("@type") == "ItemList":
                for item in data.get("itemListElement", []):
                    url = item.get("url", "")
                    if "/reviews/albums/" in url:
                        slug = url.rstrip("/").split("/")[-1]
                        name = item.get("name", "").strip("*").strip()
                        reviews.append({
                            "name": name,
                            "url": url,
                            "slug": slug,
                            "position": item.get("position", 0),
                        })
                break
        except:
            pass
    
    return reviews


def parse_album_detail(html_text, url):
    """解析专辑详情页"""
    result = {
        "url": url,
        "album": None, "artist": None,
        "pitchfork_score": None,
        "reader_score": None, "reader_count": None,
        "genre": None, "label": None,
        "release_date": None, "author": None, "review_date": None,
        "bnm": False, "bnr": False,
    }
    
    # Album (h1 title)
    m = re.search(r'<h1[^>]*>\s*<span[^>]*>([^<]+)</span>', html_text)
    if m:
        result["album"] = m.group(1).strip()
    
    # Artist
    m = re.search(r'<a href="/artists/[^"]+/"[^>]*>([^<]+)</a>', html_text)
    if m:
        result["artist"] = m.group(1).strip()
    
    # Pitchfork score: "Pitchfork score" 标记后紧跟的数字
    m = re.search(r'Pitchfork score</[^>]*>\s*<[^>]*>\s*<[^>]*>\s*([\d]\.[\d])', html_text, re.DOTALL)
    if not m:
        m = re.search(r'Pitchfork score[^<]{0,300}([\d]\.[\d])', html_text)
    result["pitchfork_score"] = m.group(1) if m else None
    
    # Reader score + count
    m = re.search(r'Based on (\d+) readers', html_text)
    if m:
        result["reader_count"] = int(m.group(1))
        rest = html_text[m.end():m.end()+500]
        sm = re.search(r'([\d]\.[\d])', rest)
        if sm:
            result["reader_score"] = sm.group(1)
    
    # BNM / BNR
    result["bnm"] = bool(re.search(r'Best New Music', html_text))
    result["bnr"] = bool(re.search(r'Best New Reissue', html_text))
    
    # Genre
    m = re.search(r'<a href="/genre/[^"]+/"[^>]*>([^<]+)</a>', html_text)
    if m:
        result["genre"] = m.group(1).strip()
    
    # Label
    m = re.search(r'<a href="/label/[^"]+/"[^>]*>([^<]+)</a>', html_text)
    if m:
        result["label"] = m.group(1).strip()
    
    # Release Date
    m = re.search(r'Re lease Date[^<]*<[^>]*>\s*<[^>]*>\s*([^<]{1,50})', html_text, re.DOTALL)
    if m:
        result["release_date"] = m.group(1).strip()
    
    # Author
    m = re.search(r'By\s+<a[^>]+>([^<]+)</a>', html_text)
    if m:
        result["author"] = m.group(1).strip()
    
    # Review date
    m = re.search(r'Re viewed\s+([^<\n]+)', html_text)
    if m:
        result["review_date"] = m.group(1).strip()
    
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", type=int, default=1)
    parser.add_argument("--url", default="https://pitchfork.com/reviews/albums/")
    parser.add_argument("--test-detail")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    
    print("[Pitchfork] 启动 CloakBrowser...")
    browser = launch(headless=False)
    page = browser.new_page()
    
    # 过 CF
    print("[Pitchfork] 访问首页过 CF...")
    page.goto("https://pitchfork.com")
    time.sleep(8)
    
    if args.test_detail:
        # 测试专辑详情页
        print(f"[Pitchfork] 测试详情页: {args.test_detail}")
        url = args.test_detail
        page.evaluate(f"window.location.href = '{url}'")
        time.sleep(5)
        detail = parse_album_detail(page.content(), url)
        print(json.dumps(detail, ensure_ascii=False, indent=2))
    else:
        # 抓列表页
        list_url = args.url
        all_reviews = []
        
        for page_num in range(1, args.pages + 1):
            page_url = list_url if page_num == 1 else f"{list_url}?page={page_num}"
            print(f"\n=== Page {page_num}: {page_url} ===")
            page.evaluate(f"window.location.href = '{page_url}'")
            time.sleep(6)
            
            html = page.content()
            reviews = parse_album_list(html)
            print(f"  找到 {len(reviews)} 条")
            all_reviews.extend(reviews)
        
        print(f"\n=== 共 {len(all_reviews)} 条，开始抓详情 ===")
        details = []
        for i, rev in enumerate(all_reviews[:5]):
            print(f"  [{i+1}/{min(len(all_reviews),5)}] {rev['name'][:50]}...", end="", flush=True)
            try:
                page.evaluate(f"window.location.href = '{rev['url']}'")
                time.sleep(4)
                detail = parse_album_detail(page.content(), rev["url"])
                detail["name"] = rev["name"]
                detail["position"] = rev["position"]
                details.append(detail)
                print(f" PF={detail['pitchfork_score']} BNM={detail['bnm']}")
            except Exception as e:
                print(f" FAIL: {e}")
        
        # 保存
        ts = time.strftime("%Y%m%d_%H%M%S")
        out_file = args.output or os.path.join(OUTPUT_DIR, f"albums_{ts}.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(details, f, ensure_ascii=False, indent=2)
        print(f"\nSaved: {out_file}")
    
    browser.close()


if __name__ == "__main__":
    main()