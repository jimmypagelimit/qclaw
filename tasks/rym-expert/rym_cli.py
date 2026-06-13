#!/usr/bin/env python3
"""
RYM Expert CLI - 统一的 RateYourMusic 抓取工具（CloakBrowser 版）

用法:
  python rym_cli.py search "Twin Fantasy" "Car Seat Headrest"
  python rym_cli.py genre-tree rock
  python rym_cli.py charts --year 2026
  python rym_cli.py fill-db --limit 50
"""
import argparse, json, os, re, sys, time, sqlite3
import cloakbrowser
from pathlib import Path
from datetime import datetime

# 配置
DB_PATH = Path(r"C:\Users\qujt\.qclaw\workspace\_music_latest.db")
RYM_DIR = Path(r"C:\Users\qujt\.qclaw\workspace\tasks\rym-expert")
DATA_DIR = RYM_DIR / "data"
DOCS_DIR = RYM_DIR / "docs"

for d in [DATA_DIR, DOCS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


class RYMClient:
    """RYM 抓取客户端"""
    
    def __init__(self, headless=False):
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
    
    def launch(self):
        """启动 CloakBrowser（headless=False 必须）"""
        try:
            self.browser = cloakbrowser.launch(headless=self.headless)
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
            return True
        except Exception as e:
            print(f"[ERROR] launch 失败: {e}")
            return False
    
    def close(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()
            self.browser = None
    
    def visit_home(self, wait=20):
        """访问首页并等待 CF challenge"""
        self.page.goto("https://rateyourmusic.com/", wait_until="domcontentloaded")
        time.sleep(wait)
        html = self.page.content()
        return len(html) > 80000
    
    def navigate_js(self, path, wait=25):
        """用 JS location.href 导航（绕 CF 503）"""
        url = f"https://rateyourmusic.com{path}"
        self.page.evaluate(f'location.href = "{url}"')
        time.sleep(wait)
        html = self.page.content()
        return len(html) > 80000
    
    def search_album(self, album, artist):
        """搜索专辑，返回最佳匹配"""
        if not self.launch():
            return None
        
        try:
            # 1. 首页过 CF
            if not self.visit_home():
                print("[WARN] CF challenge 未完成")
                return None
            
            # 2. 输入搜索
            search_q = f"{artist} {album}"
            self.page.fill("#ui_search_input_main_search", "")
            time.sleep(1)
            self.page.type("#ui_search_input_main_search", search_q, delay=60)
            time.sleep(2)
            self.page.click('button[type="submit"]')
            time.sleep(5)
            
            # 3. 提取搜索结果
            html = self.page.content()
            results = self._parse_search_results(html)
            
            # 4. 找最佳匹配并进入专辑页
            best = self._find_best_match(results, album, artist)
            if best:
                # JS click 进入专辑页
                if self._click_album_link(best['url']):
                    album_html = self.page.content()
                    details = self._parse_album_page(album_html)
                    best.update(details)
                    return best
            
            return None
            
        finally:
            self.close()
    
    def _parse_search_results(self, html):
        """解析搜索结果"""
        results = []
        # 提取所有 release 链接
        pattern = r'href="(/release/album/[^"]+)"[^>]*>([^<]+)</a>'
        for m in re.finditer(pattern, html):
            results.append({
                'url': m.group(1),
                'album': m.group(2).strip(),
                'artist': ''
            })
        
        # 尝试提取艺人名（上下文搜索）
        for r in results:
            idx = html.find(r['url'])
            if idx > 0:
                # 向前搜索艺人名
                ctx_start = max(0, idx - 300)
                ctx = html[ctx_start:idx]
                artist_m = re.search(r'>([^<]{2,50})</a>\s*-\s*$', ctx)
                if artist_m:
                    r['artist'] = artist_m.group(1).strip()
        
        return results
    
    def _find_best_match(self, results, album, artist):
        """最佳匹配"""
        al, ar = album.lower(), artist.lower()
        for r in results:
            rl, rr = r['album'].lower(), r['artist'].lower()
            if ar in rr or rr in ar:
                if al in rl or rl in al:
                    return r
        return results[0] if results else None
    
    def _click_album_link(self, url):
        """用 JS 点击链接进入专辑页（避免 page.goto 的 503）"""
        try:
            # 找到链接元素并 JS 点击
            self.page.evaluate(f'''
                const links = document.querySelectorAll('a[href="{url}"]');
                if (links.length > 0) links[0].click();
            ''')
            time.sleep(5)
            return True
        except:
            return False
    
    def _parse_album_page(self, html):
        """解析专辑详情页（正则 from page.content）"""
        details = {}
        
        # 评分
        m = re.search(r'RYM Rating: ([\d.]+)', html)
        if m:
            details['rating'] = float(m.group(1))
        
        # 评价数
        m = re.search(r'([\d,]+) ratings', html)
        if m:
            details['ratings_count'] = int(m.group(1).replace(',', ''))
        
        # 流派
        genres = re.findall(r'href="/genre/[^"]+">([^<]+)</a>', html)
        if genres:
            details['genres'] = list(set(genres))
        
        return details
    
    def get_genre_tree(self, genre_slug):
        """获取流派子流派树"""
        if not self.launch():
            return None
        
        try:
            if not self.visit_home():
                return None
            
            if not self.navigate_js(f"/genre/{genre_slug}/"):
                return None
            
            html = self.page.content()
            return self._parse_genre_page(html, genre_slug)
            
        finally:
            self.close()
    
    def _parse_genre_page(self, html, genre_slug):
        """解析流派页，提取所有子流派"""
        children = []
        pattern = f'href="/genre/([^"]+)"[^>]*>([^<]+)</a>'
        
        for m in re.finditer(pattern, html):
            slug, name = m.groups()
            # 只保留包含父流派的子流派
            if genre_slug in slug and slug != genre_slug:
                children.append({
                    'slug': slug,
                    'name': name.strip()
                })
        
        # 去重
        seen = set()
        unique = []
        for c in children:
            if c['slug'] not in seen:
                seen.add(c['slug'])
                unique.append(c)
        
        return {
            'genre': genre_slug,
            'children': unique,
            'count': len(unique)
        }
    
    def get_charts(self, year):
        """获取年度榜单（前50）"""
        if not self.launch():
            return None
        
        try:
            if not self.visit_home():
                return None
            
            charts_url = f"/charts/chart_view?a=custom_chart&chart_type=album&year={year}"
            if not self.navigate_js(charts_url):
                return None
            
            html = self.page.content()
            return self._parse_charts(html, year)
            
        finally:
            self.close()
    
    def _parse_charts(self, html, year):
        """解析榜单"""
        albums = []
        # 提取榜单条目
        pattern = r'class="chart_item[^>]*>.*?class="release"[^>]*>([^<]+)</a>.*?class="artist"[^>]*>([^<]+)</a>.*?([\d.]+)\s+avg'
        
        for i, m in enumerate(re.finditer(pattern, html, re.DOTALL)):
            if i >= 50:
                break
            albums.append({
                'rank': i + 1,
                'album': m.group(1).strip(),
                'artist': m.group(2).strip(),
                'rating': float(m.group(3)),
                'year': year
            })
        
        return {'year': year, 'count': len(albums), 'albums': albums}


def cmd_search(args):
    """搜索命令"""
    client = RYMClient(headless=False)
    result = client.search_album(args.album, args.artist)
    if result:
        print("=== 搜索结果 ===")
        print(f"专辑: {result.get('album')}")
        print(f"艺人: {result.get('artist')}")
        print(f"RYM 评分: {result.get('rating')}")
        print(f"评价数: {result.get('ratings_count')}")
        print(f"流派: {', '.join(result.get('genres', []))}")
        print(f"URL: {result.get('url')}")
    else:
        print("未找到")


def cmd_genre_tree(args):
    """流派树命令"""
    client = RYMClient(headless=False)
    result = client.get_genre_tree(args.genre)
    if result:
        print(f"=== {args.genre} 流派树 ===")
        print(f"共 {result['count']} 个子流派")
        for c in result['children'][:20]:
            print(f"  - {c['name']} ({c['slug']})")
        if result['count'] > 20:
            print(f"  ... 还有 {result['count'] - 20} 个")
    else:
        print("获取失败")


def cmd_charts(args):
    """榜单命令"""
    client = RYMClient(headless=False)
    result = client.get_charts(args.year)
    if result:
        out_file = DATA_DIR / f"charts-yearly/{args.year}/{args.year}.json"
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"[RYM] {args.year} 年榜已保存: {out_file} ({result['count']} 张)")


def cmd_fill_db(args):
    """数据库回填命令"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # 找无 RYM 评分的专辑
    rows = conn.execute("""
        SELECT album_id, album_name, artist
        FROM albums
        WHERE rym_rating IS NULL
        ORDER BY album_id DESC
        LIMIT ?
    """, (args.limit,)).fetchall()
    
    print(f"[RYM] 待回填: {len(rows)} 张")
    
    client = RYMClient(headless=False)
    hits = 0
    
    for i, r in enumerate(rows):
        print(f"  [{i+1}/{len(rows)}] {r['artist'][:20]:20s} — {r['album_name'][:30]:30s}", end="", flush=True)
        
        result = client.search_album(r['album_name'], r['artist'])
        if result and 'rating' in result:
            conn.execute("""
                UPDATE albums SET rym_rating = ?, rym_ratings_count = ?, rym_url = ?
                WHERE album_id = ?
            """, (result['rating'], result.get('ratings_count'), result.get('url'), r['album_id']))
            conn.commit()
            hits += 1
            print(f" RYM={result['rating']}")
        else:
            print(" not-found")
        
        time.sleep(2)
    
    conn.close()
    print(f"[RYM] 完成: {hits}/{len(rows)}")


def main():
    parser = argparse.ArgumentParser(description="RYM Expert CLI")
    sub = parser.add_subparsers(dest="cmd")
    
    # search
    p = sub.add_parser("search")
    p.add_argument("album")
    p.add_argument("artist")
    
    # genre-tree
    p = sub.add_parser("genre-tree")
    p.add_argument("genre")
    
    # charts
    p = sub.add_parser("charts")
    p.add_argument("--year", type=int, required=True)
    
    # fill-db
    p = sub.add_parser("fill-db")
    p.add_argument("--limit", type=int, default=50)
    
    args = parser.parse_args()
    
    if args.cmd == "search":
        cmd_search(args)
    elif args.cmd == "genre-tree":
        cmd_genre_tree(args)
    elif args.cmd == "charts":
        cmd_charts(args)
    elif args.cmd == "fill-db":
        cmd_fill_db(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
