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
            await page.wait_for_timeout(8000)  # Wait for JS-rendered elements

            # Screenshot for debugging (can be removed if not needed)
            await page.screenshot(path="mobile_debug.png", full_page=True)

            # Extract title
            try:
                title = await page.locator("h1").first.inner_text()
                if not title.strip():
                    raise Exception("Empty h1")
            except:
                try:
                    title = await page.title()
                except:
                    title = "Title not found"

            # Extract UGC count from full page text
            try:
                html = await page.content()
                soup = BeautifulSoup(html, "html.parser")
                text = soup.get_text()

                match = re.search(r"([\d\.]+)([KM]?)\s+videos", text)
                if match:
                    num = float(match.group(1))
                    suffix = match.group(2)
                    multiplier = {"K": 1_000, "M": 1_000_000}.get(suffix, 1)
                    ugc_count = int(num * multiplier)
                else:
                    ugc_count = "UGC count not found"
            except Exception as e:
                ugc_count = f"Error parsing count: {e}"

        # Inside your try block after extracting `ugc_count`, add:

            try:
                match = re.search(r"([\d\.]+)([KM]?)\s+views", text)
                if match:
                    num = float(match.group(1))
                    suffix = match.group(2)
                    multiplier = {"K": 1_000, "M": 1_000_000}.get(suffix, 1)
                    total_views = int(num * multiplier)
                else:
                    total_views = "Total views not found"
            except Exception as e:
                total_views = f"Error parsing views: {e}"


        except Exception as e:
            title = "Page load failed"
            ugc_count = str(e)

        await browser.close()
        return {
            "title": title,
            "ugc_count": ugc_count,
            "total_views": total_views
        }

