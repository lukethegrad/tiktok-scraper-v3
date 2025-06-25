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
            await page.wait_for_timeout(8000)  # JS render time

            # Screenshot for debug
            await page.screenshot(path="mobile_debug.png", full_page=True)

            # Title (fallbacks)
            try:
                title = await page.locator("h1").first.inner_text()
                if not title.strip():
                    raise Exception("Empty h1")
            except:
                try:
                    title = await page.title()
                except:
                    title = "Title not found"

            # UGC Count (flexible)
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

        except Exception as e:
            title = "Page load failed"
            ugc_count = str(e)

        await browser.close()
        return {
            "title": title,
            "ugc_count": ugc_count
        }
