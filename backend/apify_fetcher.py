import os
import requests

async def fetch_top_videos_from_apify(sound_url):
    api_token = os.environ.get("APIFY_TOKEN")
    if not api_token:
        return [{"error": "APIFY_TOKEN not set"}]

    # Apify actor endpoint for TikTok scraper
    actor_id = "lukegb/tiktok-scraper"  # Replace with your actor if different
    run_url = f"https://api.apify.com/v2/actor-tasks/{actor_id}/run-sync-get-dataset-items?token={api_token}"

    # Example input (this depends on your actor config)
    payload = {
        "startUrls": [{"url": sound_url}],
        "maxVideos": 5
    }

    try:
        response = requests.post(run_url, json=payload)
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
