import os
import httpx
import asyncio

async def fetch_top_videos_from_apify(sound_url: str, max_results: int = 5):
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        return [{"error": "APIFY_TOKEN not set"}]

    headers = {"Authorization": f"Bearer {token}"}
    run_url = "https://api.apify.com/v2/acts/clockworks~tiktok-sound-scraper/runs?waitForFinish=1"
    payload = {
        "musics": [sound_url],
        "shouldDownloadCovers": False,
        "shouldDownloadVideos": False,
        "resultsPerPage": 100  # Optional: increase if needed
    }

    async with httpx.AsyncClient(timeout=120) as client:
        try:
            # Step 1: Start the Apify Actor
            run_resp = await client.post(run_url, json=payload, headers=headers)
            run_resp.raise_for_status()
            run_data = run_resp.json()
            dataset_id = run_data.get("defaultDatasetId")

            if not dataset_id:
                return [{"error": "No dataset returned"}]

            # Step 2: Fetch dataset results
            dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?clean=true"
            data_resp = await client.get(dataset_url, headers=headers)
            data_resp.raise_for_status()
            items = data_resp.json()

            # Step 3: Extract top N videos
            top_videos = []
            for item in items[:max_results]:
                top_videos.append({
                    "username": item.get("authorMeta", {}).get("name", "unknown"),
                    "views": item.get("playCount") or item.get("stats", {}).get("playCount", "N/A"),
                    "posted": item.get("createTimeISO", "N/A")
                })

            return top_videos or [{"error": "No video results found"}]

        except Exception as e:
            return [{"error": f"Apify fetch failed: {str(e)}"}]
