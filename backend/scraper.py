import asyncio
from playwright.async_api import async_playwright
import re
from bs4 import BeautifulSoup
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

            # 🧹 Dismiss popups
            try:
                cookie_button = page.locator("button:has-text('Accept')").first
                if await cookie_button.is_visible():
                    await cookie_button.click()
                    await page.wait_for_timeout(1000)
            except:
                pass

            try:
                close_app_button = page.locator("button:has-text('×')").first
                if await close_app_button.is_visible():
                    await close_app_button.click()
                    await page.wait_for_timeout(1000)
            except:
                pass

            await page.wait_for_timeout(4000)
            await page.screenshot(path="debug_full.png", full_page=True)

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

            # HTML and UGC count
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

            # 🔁 Pull top videos from Apify
            top_videos = await fetch_top_videos_from_apify(sound_url)

            return {
                "title": title,
                "ugc_count": ugc_count,
                "total_views": "View count not found",  # We may enrich this later
                "top_videos": top_videos
            }

        except Exception as e:
            # Even if Playwright fails, still try to fetch top videos from Apify
            top_videos = await fetch_top_videos_from_apify(sound_url)

            return {
                "title": "Error",
                "ugc_count": str(e),
                "total_views": str(e),
                "top_videos": top_videos
            }

        finally:
            await browser.close()
