# CloakBrowser - 诊断搜索框 + 正确选择器
from cloakbrowser import launch
import sys, time, re

sys.stdout.reconfigure(encoding='utf-8')

print("启动 CloakBrowser...")
browser = launch(headless=False)
page = browser.new_page()

# Step 1: 访问首页
print("Step 1: 访问 RYM 首页...")
page.goto("https://rateyourmusic.com/", timeout=90000)
time.sleep(20)

title = page.title()
print(f"标题: {title}")

# Step 2: 诊断搜索框 - 找所有 input 元素
print("\nStep 2: 诊断页面中的输入框...")

# 用 JavaScript 获取所有 input 元素信息
inputs_info = page.evaluate("""() => {
    const inputs = document.querySelectorAll('input');
    return Array.from(inputs).map(el => ({
        tag: el.tagName,
        type: el.type,
        id: el.id,
        name: el.name,
        className: el.className,
        placeholder: el.placeholder,
        visible: el.offsetParent !== null
    }));
}""")

print(f"找到 {len(inputs_info)} 个 input 元素:")
for inp in inputs_info:
    cls = inp.get('className', '')[:40]
    print(f"  id={inp['id']!r} name={inp['name']!r} type={inp['type']!r} class={cls!r} placeholder={inp['placeholder']!r} visible={inp['visible']}")

# Step 3: 用正确的方式定位并使用搜索框
print("\nStep 3: 使用搜索框...")

search_found = False
for inp in inputs_info:
    if inp['type'] in ('text', 'search', '') and inp['visible']:
        # 构建选择器
        if inp['id']:
            sel = f"#{inp['id']}"
        elif inp['name']:
            sel = f"input[name='{inp['name']}']"
        else:
            # 用 placeholder 或 class
            if inp['placeholder']:
                sel = f"input[placeholder='{inp['placeholder']}']"
            else:
                continue
        
        print(f"使用选择器: {sel}")
        
        try:
            search_box = page.locator(sel).first
            search_box.click()
            time.sleep(0.3)
            
            # 清空后输入
            search_box.fill("")
            search_box.type("Boys of Dungeon Lane", delay=60)
            time.sleep(0.3)
            search_box.press("Enter")
            
            search_found = True
            print("已提交搜索！等待结果...")
            break
        except Exception as e:
            print(f"  选择器失败: {e}")
            continue

if not search_found:
    # 备选：直接用 JavaScript 提交表单
    print("尝试用 JS 直接操作...")
    page.evaluate("""() => {
        const inputs = document.querySelectorAll('input[type="text"], input:not([type])');
        for (const inp of inputs) {
            if (inp.offsetParent !== null) {
                const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                nativeInputValueSetter.call(inp, 'Boys of Dungeon Lane');
                inp.dispatchEvent(new Event('input', { bubbles: true }));
                inp.dispatchEvent(new Event('change', { bubbles: true }));
                
                // 找到表单提交
                const form = inp.closest('form');
                if (form) form.submit();
                else inp.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', keyCode: 13, bubbles: true }));
                return true;
            }
        }
        return false;
    }""")
    search_found = True

if search_found:
    time.sleep(12)
    
    stitle = page.title()
    surl = page.url
    print(f"\n搜索结果 - 标题: {stitle}")
    print(f"URL: {surl}")
    page.screenshot(path="C:/Users/qujt/.qclaw/workspace/rym_search_v2.png")
    
    html = page.content()
    with open("C:/Users/qujt/.qclaw/workspace/rym_search_v2.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    # 如果不是错误页，找专辑链接
    if "Error" not in stitle and "error" not in surl.lower():
        # 从HTML提取 release 链接
        release_links = re.findall(r'href="(/release/[^"]+)"[^>]*>([^<]*(?:McCartney|Dungeon|Boys)[^<]*)</a>', html, re.IGNORECASE)
        print(f"\n找到 {len(release_links)} 个相关链接:")
        for href, text in release_links[:10]:
            clean_text = re.sub(r'\s+', ' ', text).strip()
            print(f"  {clean_text[:60]} -> https://rateyourmusic.com{href}")
        
        if release_links:
            target_href = release_links[0][0]
            print(f"\n导航到专辑页...")
            try:
                page.goto(f"https://rateyourmusic.com{target_href}", timeout=60000)
                time.sleep(10)
                
                atitle = page.title()
                aurl = page.url
                print(f"专辑 - 标题: {atitle}")
                print(f"URL: {aurl}")
                page.screenshot(path="C:/Users/qujt/.qclaw/workspace/rym_album_final.png", full_page=True)
                
                ahtml = page.content()
                with open("C:/Users/qujt/.qclaw/workspace/rym_album_final.html", "w", encoding="utf-8") as f:
                    f.write(ahtml)
                
                # 提取关键数据
                print("\n=== 专辑数据 ===")
                
                # RYM 评分 (通常在 .avg_rating 或类似位置)
                avg_match = re.search(r'([\d.]+)\s*/\s*5', ahtml)
                if avg_match:
                    print(f"RYM 评分: {avg_match.group(1)} / 5")
                
                # 评价数
                ratings_match = re.search(r'([\d,]+)\s*(?:ratings?|Ratings?)', ahtml)
                if ratings_match:
                    print(f"评价数: {ratings_match.group(1)}")
                
                # 流派/风格
                genres = re.findall(r'class="(?:genre|release_genre)[^"]*"[^>]*><a[^>]*>([^<]+)</a>', ahtml)
                if genres:
                    print(f"流派: {', '.join(genres)}")
                
                # 年份
                year_match = re.search(r'(?:release_year|year)[^>]*><a[^>]*>(\d{4})</a>', ahtml)
                if year_match:
                    print(f"年份: {year_match.group(1)}")
                    
            except Exception as e:
                print(f"访问失败: {e}")

browser.close()
print("\n[OK] 完成")
