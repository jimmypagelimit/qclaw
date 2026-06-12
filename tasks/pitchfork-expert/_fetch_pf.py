"""
Pitchfork Expert - 专辑评论抓取脚本 v2.1
修复: album 名通过 URL slug 匹配，HTML entity 解码，BNM 回退 HTML 搜索
"""
import sys, os, json, re, html as htmlmod, time, argparse, subprocess, codecs

sys.stdout.reconfigure(encoding="utf-8")

OUTPUT_DIR = r"C:\Users\qujt\.qclaw\workspace\tasks\pitchfork-expert\data"
os.makedirs(OUTPUT_DIR, exist_ok=True)
TEMP_HTML = r"C:\Users\qujt\.qclaw\workspace\_pf_temp.html"


def decode_str(s):
    """解码 HTML Unicode entity + Python unicode escape"""
    if not s:
        return s
    s = htmlmod.unescape(s)
    # 处理 Python repr 风格的 \uXXXX
    try:
        s = codecs.decode(s, "unicode_escape")
    except:
        pass
    # 手动替换常见 entity
    s = s.replace("\\u003C", "<").replace("\\u003E", ">")
    s = s.replace("\\u0026", "&").replace("\\u002F", "/")
    s = re.sub(r'\\u[0-9a-fA-F]{4}', lambda m: chr(int(m.group(0)[2:], 16)), s)
    s = re.sub(r'<[^>]+>', '', s).strip()
    return s


def slugify(s):
    """字符串转为 URL slug 风格用于匹配"""
    if not s:
        return ""
    s = s.lower()
    s = re.sub(r'[<em>/\\]', '', s)
    s = re.sub(r'[^a-z0-9]+', '-', s)
    s = s.strip('-')
    return s


def run_opencli(cmd, timeout=30):
    result = subprocess.run(
        f"opencli {cmd}", shell=True,
        capture_output=True, encoding="utf-8", errors="replace", timeout=timeout
    )
    return result.stdout


def get_html(url, wait=7):
    run_opencli(f"browser work open {url}", timeout=20)
    time.sleep(wait)
    run_opencli(f"browser work get html > {TEMP_HTML}", timeout=20)
    return open(TEMP_HTML, "r", encoding="utf-8", errors="replace").read()


def parse_album_detail(html_text, url, slug_from_list=None):
    result = {
        "url": url, "album": None, "artist": None,
        "pitchfork_score": None, "reader_score": None, "reader_count": None,
        "genre": None, "genres": [], "label": None, "release_date": None,
        "author": None, "review_date": None, "bnm": False, "bnr": False, "dek": None,
    }
    
    # album: 从 dangerousHed 数组中找匹配的专辑名
    # slug_from_list 是从列表页拿到的专辑名（已清洗）
    heds = re.findall(r'"dangerousHed"\s*:\s*"([^"]{5,500})"', html_text)
    if heds:
        if slug_from_list:
            # 用 URL slug 匹配（去掉 -extended 等后缀）
            target = slugify(slug_from_list)
            for h in heds:
                h_clean = decode_str(h)
                if slugify(h_clean) == target or slugify(h_clean).startswith(target[:20]):
                    result["album"] = h_clean
                    break
        if not result["album"] and len(heds) > 12:
            # 回退：用第二个 "10 to Hear" 之后的第一项
            result["album"] = decode_str(heds[12])
    
    # artist
    m = re.search(
        r'"multiReviewHeaderProps"\s*:\s*\{[^}]*"artistDetails"\s*:\s*\[\s*\{\s*"name"\s*:\s*"([^"]+)"',
        html_text, re.DOTALL
    )
    if not m:
        m = re.search(r'"artistDetails"\s*:\s*\[\s*\{\s*"name"\s*:\s*"([^"]+)"', html_text)
    result["artist"] = m.group(1) if m else None
    
    # pitchfork_score: 从 JSON "rating" 或 "score" 字段
    m = re.search(r'"rating"\s*:\s*([\d]\.[\d])', html_text)
    if not m:
        m = re.search(r'"score"\s*:\s*([\d]\.[\d])', html_text)
    result["pitchfork_score"] = m.group(1) if m else None
    
    # reader_score + count
    m = re.search(r'Based on (\d+) readers', html_text)
    if m:
        result["reader_count"] = int(m.group(1))
        rest = html_text[m.start():m.start()+3000]
        scores = re.findall(r'class="[^"]*CircularRating[^"]*"[^>]*>[^>]*>[^>]*>\s*([\d]\.[\d])', rest)
        if not scores:
            scores = re.findall(r'ListenerScore[^>]*>\s*([\d]\.[\d])\s*<', rest)
        if not scores:
            scores = re.findall(r'>(\d\.\d)<', rest[:1000])
        if scores:
            result["reader_score"] = scores[0]
    
    # BNM / BNR: 优先 JSON 字段，回退 HTML 搜索
    m = re.search(r'"isBestNewMusic"\s*:\s*(true|false)', html_text)
    if m:
        result["bnm"] = m.group(1) == "true"
    else:
        result["bnm"] = bool(re.search(r'Best New Music', html_text))
    
    m = re.search(r'"isBestNewReissue"\s*:\s*(true|false)', html_text)
    if m:
        result["bnr"] = m.group(1) == "true"
    else:
        result["bnr"] = bool(re.search(r'Best New Reissue', html_text))
    
    # genres
    genres = re.findall(r'<a href="/genre/[^"]+/"[^>]*>([^<]+)</a>', html_text)
    if genres:
        result["genre"] = genres[0]
        result["genres"] = genres[:5]
    
    # label
    labels = re.findall(r'<a href="/label/[^"]+/"[^>]*>([^<]+)</a>', html_text)
    if labels:
        result["label"] = labels[0]
    
    # release_date
    m = re.search(r'Release Date\s*</div>\s*<[^>]*>\s*<[^>]*>\s*([^<\n]{1,30})', html_text, re.DOTALL)
    if not m:
        m = re.search(r'"releaseDate[^"]*"\s*:\s*"([^"]{1,30})"', html_text)
    result["release_date"] = m.group(1).strip() if m else None
    
    # author
    m = re.search(r'"Contributors"\s*:\s*\[\s*\{\s*"name"\s*:\s*"([^"]{1,100})"', html_text)
    if not m:
        m = re.search(r'"author"\s*:\s*"([^"]{1,100})"', html_text)
    result["author"] = m.group(1).strip() if m else None
    
    # review_date
    m = re.search(r'"reviewDate"\s*:\s*"([^"]{1,50})"', html_text)
    if m:
        result["review_date"] = m.group(1)
    
    # dek: 从 multiReviewHeaderProps 提取
    m = re.search(r'"multiReviewHeaderProps"\s*:\s*\{[^}]*"dangerousDek"\s*:\s*"([^"]{10,500})"', html_text, re.DOTALL)
    if m:
        result["dek"] = htmlmod.unescape(m.group(1))
    
    return result


def parse_album_list(html_text):
    reviews = []
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
                            "name": name, "url": url, "slug": slug,
                            "position": item.get("position", 0),
                        })
                break
        except:
            pass
    return reviews


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", type=int, default=1)
    parser.add_argument("--url", default="https://pitchfork.com/reviews/albums/")
    parser.add_argument("--search")
    parser.add_argument("--output", default=None)
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()
    
    print("[Pitchfork] 开始抓取...")
    
    if args.search:
        q = args.search.replace(" ", "+")
        list_url = f"https://pitchfork.com/search/?q={q}"
    else:
        list_url = args.url
    
    all_reviews = []
    for page_num in range(1, args.pages + 1):
        page_url = list_url if page_num == 1 else f"{list_url}?page={page_num}"
        print(f"\n=== Page {page_num}: {page_url} ===")
        html = get_html(page_url, wait=7)
        print(f"  HTML 大小: {len(html)} chars")
        reviews = parse_album_list(html)
        print(f"  找到 {len(reviews)} 条评论")
        all_reviews.extend(reviews)
    
    limit = args.limit if args.limit > 0 else len(all_reviews)
    print(f"\n=== 开始抓 {min(limit, len(all_reviews))} 张专辑详情 ===")
    
    details = []
    for i, rev in enumerate(all_reviews[:limit]):
        print(f"  [{i+1}/{min(limit, len(all_reviews))}] {rev['name'][:50]}...", end="", flush=True)
        try:
            html = get_html(rev["url"], wait=5)
            detail = parse_album_detail(html, rev["url"], slug_from_list=rev["name"])
            detail["position"] = rev["position"]
            details.append(detail)
            pf = detail.get("pitchfork_score") or "N/A"
            bnm = "BNM" if detail.get("bnm") else ""
            album = (detail.get("album") or "")[:30]
            print(f" ✓ PF={pf} {bnm} | {album}")
        except Exception as e:
            print(f" ✗ {e}")
            details.append({"url": rev["url"], "name": rev["name"], "error": str(e)})
    
    ts = time.strftime("%Y%m%d_%H%M%S")
    out_file = args.output or os.path.join(OUTPUT_DIR, f"pf_albums_{ts}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(details, f, ensure_ascii=False, indent=2)
    
    pf_scores = [(d.get("album", ""), d.get("pitchfork_score")) for d in details if d.get("pitchfork_score")]
    bnm_count = sum(1 for d in details if d.get("bnm"))
    print(f"\n✓ 保存到: {out_file}")
    print(f"统计: {len(details)} 张专辑, {len(pf_scores)} 个编辑评分, {bnm_count} 个 BNM")
    for album, score in sorted(pf_scores, key=lambda x: float(x[1] or 0), reverse=True):
        print(f"  {score} - {album[:50]}")


if __name__ == "__main__":
    main()