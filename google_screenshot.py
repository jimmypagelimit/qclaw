from playwright.sync_api import sync_playwright
import os

workspace = os.environ.get("workspace_root_dir", "C:/Users/qujt/.qclaw/workspace")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.google.com", timeout=15000)
    screenshot_path = os.path.join(workspace, "google_screenshot.png")
    page.screenshot(path=screenshot_path, full_page=False)
    print(f"Screenshot saved: {screenshot_path}")
    browser.close()
