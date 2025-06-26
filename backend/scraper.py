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

            # Total views (may not be present)
            match_views = re.search(r"([\d\.]+)([KM]?)\s+views", text)
            if match_views:
                num = float(match_views.group(1))
                suffix = match_views.group(2)
                multiplier = {"K": 1_000, "M": 1_000_000}.get(suffix, 1)
                total_views = int(num * multiplier)
            else:
                total_views = "View count not found"

            # 🎯 New: Scrape top 5 videos
            video_cards = await page.locator("div[data-e2e='browse-video-item']").all()
            top_videos = []

            for video in video_cards[:5]:
                try:
                    video_link = await video.locator("a").first.get_attribute("href")
                    video_url = f"https://www.tiktok.com{video_link}"

                    vid_page = await context.new_page()
                    await vid_page.goto(video_url)
                    await vid_page.wait_for_timeout(5000)

                    # Account name
                    username = await vid_page.locator("div[data-e2e='browse-username']").inner_text()

                    # Views
                    views_text = await vid_page.locator("strong[data-e2e='video-views']").inner_text()
                    view_match = re.search(r"([\d\.]+)([KM]?)", views_text)
                    views = int(float(view_match.group(1)) * {"K": 1_000, "M": 1_000_000}.get(view_match.group(2), 1)) if view_match else None

                    # Post date
                    date_locator = vid_page.locator("span[data-e2e='browser-nickname']")
                    date_posted = await date_locator.nth(1).inner_text() if await date_locator.count() > 1 else "Date not found"

                    top_videos.append({
                        "username": username,
                        "views": views,
                        "date_posted": date_posted,
                        "video_url": video_url
                    })

                    await vid_page.close()
                except Exception:
                    continue

        except Exception as e:
            title = "Page load failed"
            ugc_count = str(e)
            total_views = str(e)
            top_videos = []


        print("\n===== HTML DUMP START =====\n")
        print(html)
        print("\n===== HTML DUMP END =====\n")
        await browser.close()
        return {
            "title": title,
            "ugc_count": ugc_count,
            "total_views": total_views,
            "top_videos": top_videos  # 🎯 return the new data
        }
