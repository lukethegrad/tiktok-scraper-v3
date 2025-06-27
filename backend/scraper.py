import asyncio
import re
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from apify_fetcher import fetch_top_videos_from_apify

async def scrape_tiktok_sound_async(sound_url):
    async with async_playwright() as p:
        iphone = p.devices["iPhone 13 Pro"]
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(**iphone)
        page = await context.new_page()

        try:
            await page.goto(sound_url, timeout=60000)
            await page.wait_for_timeout(8000)

            # 🧹 Dismiss cookie/app popups
            for text in ["Accept", "×"]:
                try:
                    button = page.locator(f"button:has-text('{text}')").first
                    if await button.is_visible():
                        await button.click()
                        await page.wait_for_timeout(1000)
                except:
                    pass

            # Debug screenshot
            await page.screenshot(path="debug_full.png", full_page=True)

            # 🎵 Extract title
            try:
                title = await page.locator("h1").first.inner_text()
                if not title.strip():
                    raise ValueError("Empty h1")
            except:
                try:
                    title = await page.title()
                except:
                    title = "Title not found"

            # 📊 Extract UGC count from page text
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text()

            match_ugc = re.search(r"([\d\.]+)([KM]?)\s+videos", text)
            if match_ugc:
                num = float(match_ugc.group(1))
                suffix = match_ugc.group(2)
                multiplier = {"K": 1_000, "M": 1_000_000}.get(suffix, 1)
                ugc_count = int(num * multiplier)
            else:
                ugc_count = "UGC count not found"

            # 📥 Fetch top videos via Apify
            top_videos = await fetch_top_videos_from_apify(sound_url)

            return {
                "title": title,
                "ugc_count": ugc_count,
                "total_views": "View count not found",  # placeholder for future enhancement
                "top_videos": top_videos
            }

        except Exception as e:
            top_videos = await fetch_top_videos_from_apify(sound_url)
            return {
                "title": "Error",
                "ugc_count": str(e),
                "total_views": str(e),
                "top_videos": top_videos
            }

        finally:
            await context.close()
            await browser.close()
