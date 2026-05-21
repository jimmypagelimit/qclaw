const { chromium } = require('playwright');

(async () => {
  // 尝试多个可能的 Chrome 路径
  const chromePaths = [
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
  ];

  let browser;
  let launchOptions = {
    headless: false,
    args: [
      '--disable-blink-features=AutomationControlled',
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-infobars',
      '--disable-blink-features',
      '--disable-features=IsolateOrigins,site-per-process',
    ]
  });

  // 绕过 webdriver 检测
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
  });

  const page = await context.newPage();

  // 通过 CDP 隐藏 navigator.webdriver
  const client = await page.context().newCDPSession(page);
  await client.send('Page.addScriptToEvaluateOnNewDocument', {
    source: `
      Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
      });
      Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5]
      });
      Object.defineProperty(navigator, 'languages', {
        get: () => ['zh-CN', 'zh', 'en-US', 'en']
      });
      window.chrome = { runtime: {} };
    `
  });

  console.log('Navigating to RYM...');
  await page.goto('https://rateyourmusic.com/charts/top/album/2026/', {
    waitUntil: 'domcontentloaded',
    timeout: 60000
  });

  // 等待页面加载，给 Cloudflare 最多 30 秒
  console.log('Waiting for page to load...');
  try {
    await page.waitForSelector('table.page_layout', { timeout: 30000 });
    console.log('✅ Page loaded successfully!');
    const title = await page.title();
    console.log('Title:', title);
    
    // 提取专辑列表
    const albums = await page.$$eval('div.chart_details h3.release', els => 
      els.map((el, i) => `${i+1}. ${el.textContent.trim()}`).slice(0, 20)
    );
    console.log('\nTop 20 Albums:');
    albums.forEach(a => console.log(a));
    
    // 保存 HTML
    const html = await page.content();
    require('fs').writeFileSync('rym_2026.html', html);
    console.log('\nHTML saved to rym_2026.html');
  } catch (e) {
    console.error('Page did not load fully:', e.message);
    // 打印当前页面内容
    const content = await page.content();
    const bodyText = await page.evaluate(() => document.body.innerText);
    console.log('Body text:', bodyText.slice(0, 500));
  }

  await browser.close();
})();
