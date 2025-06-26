import asyncio
from playwright.async_api import async_playwright
import re
from bs4 import BeautifulSoup

async def scrape_tiktok_sound_async(sound_url):
    async with async_playwright() as p:
        iphone = p.devices["iPhone 13 Pro"]
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(**iphone)
        page = await context.new_page()

        try:
            await page.goto(sound_url, timeout=60000)
            await page.wait_for_timeout(12000)

            # Screenshot to verify render
            await page.screenshot(path="debug_full.png", full_page=True)
            print("✅ Screenshot saved as debug_full.png")

            # Scroll to trigger lazy loading
            for i in range(3):
                await page.mouse.wheel(0, 3000)
                await page.wait_for_timeout(3000)

            # Optional second screenshot
            await page.screenshot(path="mobile_debug.png", full_page=True)

            # Title
            try:
                title = await page.locator("h1").first.inner_text()
                if not title.strip():
                    raise Exception("Empty h1")
            except:
                try:
                    title = await page.title()
                except:
                    title = "Title not found"

            # Full HTML for soup
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text()

            # UGC count
            match_ugc = re.search(r"([\d\.]+)([KM]?)\s+videos", text)
            if match_ugc:
                num = float(match_ugc.group(1))
                suffix = match_ugc.group(2)
                multiplier = {"K": 1_000, "M": 1_000_000}.get(suffix, 1)
                ugc_count = int(num * multiplier)
            else:
                ugc_count = "UGC count not found"

            # Total views
            match_views = re.search(r"([\d\.]+)([KM]?)\s+views", text)
            if match_views:
                num = float(match_views.group(1))
                suffix = match_views.group(2)
                multiplier = {"K": 1_000, "M": 1_000_000}.get(suffix, 1)
                total_views = int(num * multiplier)
            else:
                total_views = "View count not found"

            # Top 5 videos
            top_videos = []
            video_blocks = soup.select("div[data-e2e='sound-video-item']")
            for block in video_blocks[:5]:
                try:
                    user = block.select_one("a").get("href").split("/")[-1]
                except:
                    user = "unknown"

                try:
                    views_text = block.get_text()
                    match = re.search(r"([\d\.]+)([KM]?) views", views_text)
                    if match:
                        num = float(match.group(1))
                        suffix = match.group(2)
                        multiplier = {"K": 1_000, "M": 1_000_000}.get(suffix, 1)
                        views = int(num * multiplier)
                    else:
                        views = "N/A"
                except:
                    views = "N/A"

                top_videos.append({
                    "username": user,
                    "views": views,
                    "posted": "N/A"
                })

        except Exception as e:
            print(f"❌ Scrape failed: {e}")
            title = "Page load failed"
            ugc_count = str(e)
            total_views = str(e)
            top_videos = []

        await browser.close()
        return {
            "title": title,
            "ugc_count": ugc_count,
            "total_views": total_views,
            "top_videos": top_videos
        }
