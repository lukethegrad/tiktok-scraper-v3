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
            await page.wait_for_timeout(8000)

            # 🧹 Dismiss modals
            try:
                cookie_button = page.locator("button:has-text('Accept')").first
                if await cookie_button.is_visible():
                    await cookie_button.click()
                    await page.wait_for_timeout(1000)
                    print("✅ Dismissed cookie popup")
            except:
                print("⚠️ No cookie popup found")

            try:
                close_app_button = page.locator("button:has-text('×')").first
                if await close_app_button.is_visible():
                    await close_app_button.click()
                    await page.wait_for_timeout(1000)
                    print("✅ Dismissed 'Open in App' modal")
            except:
                print("⚠️ No app modal found")

            await page.wait_for_timeout(4000)

            # ✅ Screenshot always taken early for debugging
            try:
                await page.screenshot(path="debug_full.png", full_page=True)
                print("✅ Screenshot saved as debug_full.png")
            except Exception as e:
                print(f"❌ Screenshot save failed: {e}")

            # Scroll to trigger lazy loading
            for i in range(3):
                await page.mouse.wheel(0, 3000)
                await page.wait_for_timeout(3000)

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

            # HTML for scraping
            top_videos = []
            video_cards = await page.locator("div[data-e2e='sound-video-item']").all()
            for card in video_cards[:5]:
                try:
                    username = await card.locator("a").first.get_attribute("href")
                    username = username.split("/")[-1] if username else "unknown"
                except:
                    username = "unknown"
            
                try:
                    views_text = await card.inner_text()
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
                    "username": username,
                    "views": views,
                    "posted": "N/A"  # still to implement
                })


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
