"""
Pitchfork Expert - 用 opencli CDP 抓取专辑评论
opencli browser work 已绑定了已有 Chrome（含 Pitchfork 登录态）
"""
import sys, os, json, re, time, argparse, subprocess

sys.stdout.reconfigure(encoding="utf-8")

OUTPUT_DIR = r"C:\Users\qujt\.qclaw\workspace\tasks\pitchfork-expert\data"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def run_opencli(cmd, timeout=30):
    """执行 opencli 命令并返回 stdout"""
    full_cmd = f'opencli {cmd}'
    result = subprocess.run(
        full_cmd, shell=True, capture_output=True,
        encoding="utf-8", errors="replace", timeout=timeout
    )
    return result.stdout + result.stderr


def wait_load(sec=6):
    """等待页面加载"""
    time.sleep(sec)


def parse_album_list(html_text):
    """解析列表页"""
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
    
    # Album title
    m = re.search(r'<h1[^>]*>\s*<span[^>]*>([^<]+)</span>', html_text)
    if m:
        result["album"] = m.group(1).strip()
    
    # Artist
    m = re.search(r'<a href="/artists/[^"]+/"[^>]*>([^<]+)</a>', html_text)
    if m:
        result["artist"] = m.group(1).strip()
    
    # Pitchfork score: 找 "Pitchfork score" 后的数字
    m = re.search(r'Pitchfork score[^<]{0,500}([\d]\.[\d])', html_text)
    if not m:
        m = re.search(r'class="[^\"]*pitchfork[^\"]*score[^\"]*"[^>]*>\s*([\d]\.[\d])', html_text)
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
    
    # 确保绑定到 opencli 的 Chrome
    print("[Pitchfork] 检查浏览器绑定...")
    status = run_opencli("browser work state", timeout=10)
    print(f"  状态: {status[:100]}")
    
    if args.test_detail:
        # 测试专辑详情页
        print(f"[Pitchfork] 测试详情页: {args.test_detail}")
        url = args.test_detail
        run_opencli(f'browser work open {url}', timeout=20)
        wait_load(6)
        run_opencli('browser work extract', timeout=15)
        html = run_opencli('browser work get html', timeout=15)
        detail = parse_album_detail(html, url)
        print(json.dumps(detail, ensure_ascii=False, indent=2))
    else:
        # 抓列表页
        list_url = args.url
        all_reviews = []
        
        for page_num in range(1, args.pages + 1):
            page_url = list_url if page_num == 1 else f"{list_url}?page={page_num}"
            print(f"\n=== Page {page_num}: {page_url} ===")
            run_opencli(f'browser work open {page_url}', timeout=20)
            wait_load(6)
            
            html = run_opencli('browser work get html', timeout=15)
            reviews = parse_album_list(html)
            print(f"  找到 {len(reviews)} 条")
            all_reviews.extend(reviews)
        
        print(f"\n=== 共 {len(all_reviews)} 条，开始抓详情 ===")
        details = []
        for i, rev in enumerate(all_reviews[:5]):
            print(f"  [{i+1}/{min(len(all_reviews),5)}] {rev['name'][:50]}...", end="", flush=True)
            try:
                run_opencli(f'browser work open {rev["url"]}', timeout=20)
                wait_load(5)
                html = run_opencli('browser work get html', timeout=15)
                detail = parse_album_detail(html, rev["url"])
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


if __name__ == "__main__":
    main()