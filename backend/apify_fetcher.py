import os
import requests

APIFY_TOKEN = os.environ.get("APIFY_TOKEN")


def fetch_top_videos_from_apify(sound_url, max_videos=5):
    if not APIFY_TOKEN:
        raise Exception("APIFY_TOKEN not set in environment")

    payload = {
        "startUrls": [{"url": sound_url}],
        "maxVideos": max_videos
    }

    response = requests.post(
        "https://api.apify.com/v2/actor-tasks/apify/tiktok-scraper/runs?token=" + APIFY_TOKEN,
        json=payload
    )

    if response.status_code != 201:
        raise Exception("Failed to start Apify actor: " + response.text)

    run_id = response.json()["data"]["id"]

    # Poll for result
    for _ in range(30):
        result = requests.get(
            f"https://api.apify.com/v2/actor-runs/{run_id}/dataset/items?token={APIFY_TOKEN}"
        )
        if result.status_code == 200 and result.json():
            videos = result.json()
            return [
                {
                    "username": v.get("author", {}).get("uniqueId", "unknown"),
                    "views": v.get("stats", {}).get("playCount", "N/A"),
                    "posted": v.get("createTime", "N/A")
                }
                for v in videos[:max_videos]
            ]
    return []
