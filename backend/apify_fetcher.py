import os
import asyncio
from apify_client import ApifyClient

async def fetch_top_videos_from_apify(sound_url):
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        return [{"error": "APIFY_TOKEN not set"}]

    client = ApifyClient(token)

    try:
        run_input = { "musics": [sound_url] }
        run = await client.actor("clockworks/tiktok-sound-scraper").call(run_input=run_input)

        dataset_id = run.get("defaultDatasetId")
        if not dataset_id:
            return [{"error": "No dataset returned"}]

        dataset = client.dataset(dataset_id)
        items = await dataset.list_items()
        videos = []

        for item in items["items"]:
            videos.append({
                "username": item.get("authorMeta", {}).get("name", "unknown"),
                "views": item.get("stats", {}).get("playCount", "N/A"),
                "posted": item.get("createTimeISO", "N/A")
            })
            if len(videos) >= 5:
                break

        return videos

    except Exception as e:
        return [{"error": str(e)}]
