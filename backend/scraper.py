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

            # HTML + raw text for scraping
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

            # 🎯 NEW: Total views
            match_views = re.search(r"([\d\.]+)([KM]?)\s+views", text)
            if match_views:
                num = float(match_views.group(1))
                suffix = match_views.group(2)
                multiplier = {"K": 1_000, "M": 1_000_000}.get(suffix, 1)
                total_views = int(num * multiplier)
            else:
                total_views = "View count not found"

        except Exception as e:
            title = "Page load failed"
            ugc_count = str(e)
            total_views = str(e)

        await browser.close()
        return {
            "title": title,
            "ugc_count": ugc_count,
            "total_views": total_views  # 🎯 include this
        }
