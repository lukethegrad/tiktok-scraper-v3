import asyncio
from playwright.async_api import async_playwright
import re

async def scrape_tiktok_sound_async(sound_url):
    async with async_playwright() as p:
        iphone = p.devices["iPhone 13 Pro"]
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(**iphone)
        page = await context.new_page()

        title = "Title not found"
        ugc_count = "UGC count not found"
        total_views = "View count not found"
        top_videos = []

        try:
            await page.goto(sound_url, timeout=60000)
            await page.wait_for_timeout(8000)

            # ⛔ Try dismissing cookie banner
            try:
                cookie_btn = page.locator('button:has-text("Allow all")')
                if await cookie_btn.is_visible():
                    await cookie_btn.click()
                    await page.wait_for_timeout(1000)
                    print("✅ Dismissed cookie banner")
            except:
                print("⚠️ Cookie banner not found")

            # ⛔ Try dismissing TikTok app modal
            try:
                close_btn = page.locator('button[aria-label="Close"]')
                if await close_btn.is_visible():
                    await close_btn.click()
                    await page.wait_for_timeout(1000)
                    print("✅ Dismissed app modal")
            except:
                print("⚠️ App modal not found")

            await page.wait_for_timeout(3000)

            # 🎯 Grab title
            try:
                title = await page.locator("h1").first.inner_text()
            except:
                try:
                    title = await page.title()
                except:
                    pass

            # 🌀 Scroll to load content
            for _ in range(3):
                await page.mouse.wheel(0, 3000)
                await page.wait_for_timeout(2000)

            # ✅ Screenshot
            try:
                await page.screenshot(path="debug_full.png", full_page=True)
            except:
                pass

            # 🧠 Try extracting video data
            cards = await page.locator("div[data-e2e='sound-video-item']").all()
            for card in cards[:5]:
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
                        mult = {"K": 1_000, "M": 1_000_000}.get(match.group(2), 1)
                        views = int(num * mult)
                    else:
                        views = "N/A"
                except:
                    views = "N/A"

                top_videos.append({
                    "username": username,
                    "views": views,
                    "posted": "N/A"
                })

            # 🧮 UGC + views (fallback: page text)
            text = await page.inner_text("body")
            match_ugc = re.search(r"([\d\.]+)([KM]?)\s+videos", text)
            if match_ugc:
                num = float(match_ugc.group(1))
                suffix = match_ugc.group(2)
                ugc_count = int(num * {"K": 1_000, "M": 1_000_000}.get(suffix, 1))

            match_views = re.search(r"([\d\.]+)([KM]?)\s+views", text)
            if match_views:
                num = float(match_views.group(1))
                suffix = match_views.group(2)
                total_views = int(num * {"K": 1_000, "M": 1_000_000}.get(suffix, 1))

        except Exception as e:
            print(f"❌ Scrape failed: {e}")

        await browser.close()
        return {
            "title": title,
            "ugc_count": ugc_count,
            "total_views": total_views,
            "top_videos": top_videos
        }
