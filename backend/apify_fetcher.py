import os
import httpx

async def fetch_top_videos_from_apify(sound_url):
    api_token = os.environ.get("APIFY_TOKEN")
    if not api_token:
        return [{"error": "APIFY_TOKEN not set"}]

    actor_id = "clockworks/tiktok-sound-scraper"  # Replace if needed
    run_url = f"https://api.apify.com/v2/actor-tasks/{actor_id}/run-sync-get-dataset-items?token={api_token}"

    payload = {
        "startUrls": [{"url": sound_url}],
        "maxVideos": 5
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(run_url, json=payload)
            response.raise_for_status()
            items = response.json()

        top_videos = []
        for item in items[:5]:
            top_videos.append({
                "username": item.get("authorUniqueId", "unknown"),
                "views": item.get("stats", {}).get("playCount", "N/A"),
                "posted": item.get("createTime", "N/A")
            })
        return top_videos

    except Exception as e:
        return [{"error": str(e)}]
