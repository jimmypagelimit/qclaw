"""
Pitchfork Expert - 专辑评论抓取 (CloakBrowser 方案)
用法:
  单页:   python _fetch_album_reviews.py
  多页:   python _fetch_album_reviews.py --pages 5
  搜索:   python _fetch_album_reviews.py --search "car seat headrest"
  指定页: python _fetch_album_reviews.py --url "https://pitchfork.com/reviews/albums/"
"""
import sys, os, json, re, time, argparse, urllib.parse
sys.path.insert(0, r"C:\Users\qujt\.qclaw\workspace")
from rym_tool import launch_browser # 复用 RYM 项目的 CloakBrowser 方案

sys.stdout.reconfigure(encoding="utf-8")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml",
}
OUTPUT_DIR = r"C:\Users\qujt\.qclaw\workspace\tasks\pitchfork-expert\data"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def fetch_page(browser, url, wait=6):
    """用 JS location.href 绕过 CF 加载页面"""
    browser.get(url, headers=HEADERS)
    time.sleep(wait)
    # 用 JS 导航绕过 CF
    browser.evaluate(f"window.location.href = '{url}'")
    time.sleep(wait)
    return browser


def parse_album_list(html_text):
    """解析 Pitchfork 专辑列表页"""
    reviews = []
    
    # 1. JSON-LD ItemList (主要来源)
    jsonld_blocks = re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', html_text, re.DOTALL
    )
    item_list = []
    for block in jsonld_blocks:
        try:
            data = json.loads(block)
            if data.get("@type") == "ItemList":
                item_list = data.get("itemListElement", [])
                break
        except:
            pass
    
    # 2. 从 JSON-LD 提取 URL
    for item in item_list:
        url = item.get("url", "")
        name = item.get("name", "")
        pos = item.get("position", 0)
        if "/reviews/albums/" in url:
            # 从 URL 中提取 slug
            slug = url.rstrip("/").split("/")[-1]
            reviews.append({
                "name": name.strip("*").strip(),
                "url": url,
                "slug": slug,
                "position": pos,
                "source": "jsonld"
            })
    
    # 3. 从 HTML 补充（备选）
    # 评分在列表页无法直接获取，需进入专辑页
    
    return reviews


def parse_album_detail(html_text, url):
    """解析专辑详情页，提取所有元数据"""
    result = {
        "url": url,
        "album": None, "artist": None, "pitchfork_score": None,
        "reader_score": None, "reader_count": None,
        "genre": None, "label": None, "release_date": None,
        "author": None, "review_date": None,
        "bnm": False, "bnr": False,
        "content_snippet": None,
        "html_size": len(html_text)
    }
    
    # Album name: <h1> in review header
    m = re.search(r'<h1[^>]*class="[^\"]*title[^\"]*"[^>]*>\s*<span[^>]*>\s*([^<]+)\s*</span>', html_text)
    if m:
        result["album"] = m.group(1).strip()
    else:
        m = re.search(r'<h1[^>]*>\s*<span[^>]*>\s*([^<]+)\s*</span>', html_text)
        if m:
            result["album"] = m.group(1).strip()
    
    # Artist: link to /artists/
    m = re.search(r'<a href="/artists/[^"]+/"[^>]*>([^<]+)</a>', html_text)
    if m:
        result["artist"] = m.group(1).strip()
    
    # Pitchfork score: 8.0 出现在 "Pitchfork score" 标记之后
    m = re.search(r'Pitchfork score</[^>]*>[^<]*<[^>]*>\s*([\d]\.[\d])', html_text, re.DOTALL)
    if not m:
        m = re.search(r'Pitchfork\s+score[^<]*<[^>]*>\s*([\d]\.[\d])', html_text)
    if not m:
        # 尝试找大字体评分
        m = re.search(r'class="[^\"]*pitchfork[^\"]*score[^\"]*"[^>]*>\s*([\d]\.[\d])', html_text)
    result["pitchfork_score"] = m.group(1) if m else None
    
    # Reader score
    m = re.search(r'Based on (\d+) readers[^>]*>[^>]*>\s*([\d]\.[\d])', html_text, re.DOTALL)
    if not m:
        m = re.search(r'Based on (\d+) readers', html_text)
        if m:
            count = int(m.group(1))
            # 找紧跟的评分
            rest = html_text[m.end():m.end()+200]
            sm = re.search(r'([\d]\.[\d])', rest)
            if sm:
                result["reader_score"] = sm.group(1)
                result["reader_count"] = count
    else:
        result["reader_count"] = int(m.group(1))
        result["reader_score"] = m.group(2)
    
    # Best New Music / Reissue
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
    m = re.search(r'Release Date[^<]*<[^>]*>\s*<[^>]*>\s*([^<]+)', html_text, re.DOTALL)
    if m:
        result["release_date"] = m.group(1).strip()
    
    # Author
    m = re.search(r'By\s+<a[^>]+>([^<]+)</a>', html_text)
    if m:
        result["author"] = m.group(1).strip()
    
    # Review date
    m = re.search(r'Reviewed\s+([^<\n]+)', html_text)
    if m:
        result["review_date"] = m.group(1).strip()
    
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", type=int, default=1)
    parser.add_argument("--url", default="https://pitchfork.com/reviews/albums/")
    parser.add_argument("--search")
    parser.add_argument("--output", default=None)
    parser.add_argument("--wait", type=int, default=6)
    args = parser.parse_args()
    
    # 目标 URL
    if args.search:
        q = urllib.parse.quote(args.search)
        list_url = f"https://pitchfork.com/search/?q={q}"
    else:
        list_url = args.url
    
    print(f"[Pitchfork] 启动浏览器...")
    browser = launch_browser()
    print(f"[Pitchfork] 访问首页过 CF...")
    browser.get("https://pitchfork.com", timeout=30)
    time.sleep(8)
    
    all_reviews = []
    
    for page in range(1, args.pages + 1):
        page_url = list_url if page == 1 else f"{list_url}?page={page}"
        print(f"\n=== Page {page}: {page_url} ===")
        
        # 用 JS 导航
        browser.evaluate(f"window.location.href = '{page_url}'")
        time.sleep(args.wait)
        
        html = browser.page.content()
        print(f"  HTML 大小: {len(html)} chars")
        
        if page == 1:
            reviews = parse_album_list(html)
            print(f"  找到 {len(reviews)} 条评论")
            all_reviews.extend(reviews)
        else:
            reviews = parse_album_list(html)
            print(f"  找到 {len(reviews)} 条评论")
            all_reviews.extend(reviews)
    
    print(f"\n=== 共 {len(all_reviews)} 条评论，开始抓详情 ===")
    
    details = []
    for i, rev in enumerate(all_reviews):
        print(f"  [{i+1}/{len(all_reviews)}] {rev['name'][:50]}...", end="", flush=True)
        try:
            browser.evaluate(f"window.location.href = '{rev['url']}'")
            time.sleep(5)
            detail = parse_album_detail(browser.page.content(), rev["url"])
            detail["position"] = rev["position"]
            details.append(detail)
            print(f" ✓ PF={detail['pitchfork_score']} BNM={detail['bnm']}")
        except Exception as e:
            print(f" ✗ {e}")
            details.append({"url": rev["url"], "name": rev["name"], "error": str(e)})
        
        if (i + 1) % 10 == 0:
            print(f"  --- 进度: {i+1}/{len(all_reviews)} ---")
    
    browser.close()
    
    # 保存
    ts = time.strftime("%Y%m%d_%H%M%S")
    out_file = args.output or os.path.join(OUTPUT_DIR, f"albums_{ts}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(details, f, ensure_ascii=False, indent=2)
    print(f"\n✓ 保存到: {out_file}")
    
    # 统计
    pf_scores = [d["pitchfork_score"] for d in details if d.get("pitchfork_score")]
    bnm_count = sum(1 for d in details if d.get("bnm"))
    print(f"统计: {len(details)} 张专辑, {len(pf_scores)} 个编辑评分, {bnm_count} 个 BNM")


if __name__ == "__main__":
    main()