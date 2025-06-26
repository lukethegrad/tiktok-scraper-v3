import asyncio
from playwright.async_api import async_playwright
import re

async def scrape_tiktok_sound_async(sound_url):
    async with async_playwright() as p:
        iphone = p.devices["iPhone 13 Pro"]
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(**iphone)
        page = await context.new_page()

        try:
            await page.goto(sound_url, timeout=60000)
            await page.wait_for_timeout(8000)

            # Dismiss modals
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

            # Screenshot for debugging
            try:
                await page.screenshot(path="debug_full.png", full_page=True)
                print("✅ Screenshot saved as debug_full.png")
            except Exception as e:
                print(f"❌ Screenshot save failed: {e}")

            # Scroll to load videos
            for _ in range(3):
                await page.mouse.wheel(0, 3000)
                await page.wait_for_timeout(3000)

            # Title
            try:
                title = await page.locator("h1").first.inner_text()
                if not title.strip():
                    raise Exception("Empty h1")
            except:
                title = await page.title() or "Title not found"

            # Page text for global counts
            text = await page.inner_text("body")

            # UGC count
            match_ugc = re.search(r"([\d\.]+)([KM]?)\s+videos", text)
            if match_ugc:
                num = float(match_ugc.group(1))
                suffix = match_ugc.group(2)
                ugc_count = int(num * {"K": 1_000, "M": 1_000_000}.get(suffix, 1))
            else:
                ugc_count = "UGC count not found"

            # Total views (if shown)
            match_views = re.search(r"([\d\.]+)([KM]?)\s+views", text)
            if match_views:
                num = float(match_views.group(1))
                suffix = match_views.group(2)
                total_views = int(num * {"K": 1_000, "M": 1_000_000}.get(suffix, 1))
            else:
                total_views = "View count not found"

            # Get top video links
            video_cards = await page.locator("div[data-e2e='sound-video-item'] a").all()
            video_urls = []
            for a in video_cards:
                href = await a.get_attribute("href")
                if href and href.startswith("/video/"):
                    video_urls.append("https://www.tiktok.com" + href)

            # Visit each video to get data
            top_videos = []
            for url in video_urls[:5]:
                try:
                    video_page = await context.new_page()
                    await video_page.goto(url, timeout=30000)
                    await video_page.wait_for_timeout(5000)

                    # Views
                    body_text = await video_page.inner_text("body")
                    match = re.search(r"([\d\.]+)([KM]?) views", body_text)
                    if match:
                        num = float(match.group(1))
                        suffix = match.group(2)
                        views = int(num * {"K": 1_000, "M": 1_000_000}.get(suffix, 1))
                    else:
                        views = "N/A"

                    # Username
                    try:
                        username = await video_page.locator("a[href*='/@']").first.inner_text()
                    except:
                        username = "unknown"

                    top_videos.append({
                        "username": username,
                        "views": views,
                        "posted": "N/A"  # Optional enhancement
                    })

                    await video_page.close()
                except Exception as e:
                    print(f"⚠️ Failed to scrape {url}: {e}")
                    top_videos.append({
                        "username": "unknown",
                        "views": "N/A",
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
