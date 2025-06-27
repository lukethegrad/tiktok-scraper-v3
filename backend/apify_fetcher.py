import os
import httpx
import asyncio

async def fetch_top_videos_from_apify(sound_url):
    token = os.environ.get("APIFY_TOKEN")
    if not token:
        return [{"error": "APIFY_TOKEN not set"}]

    # 1. Run actor
    run_url = "https://api.apify.com/v2/acts/clockworks~tiktok-sound-scraper/runs?waitForFinish=1"
    headers = {"Authorization": f"Bearer {token}"}
    payload = { "musics": [sound_url] }

    async with httpx.AsyncClient() as client:
        try:
            run_resp = await client.post(run_url, json=payload, headers=headers)
            run_resp.raise_for_status()
            run_data = run_resp.json()
            dataset_id = run_data.get("defaultDatasetId")
            if not dataset_id:
                print("❌ No dataset ID returned from Apify run")
                return [{"error": "No dataset returned"}]

            print("✅ Apify run completed. Dataset ID:", dataset_id)

            # 2. Fetch dataset items
            dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?clean=true"
            dataset_resp = await client.get(dataset_url, headers=headers)
            dataset_resp.raise_for_status()
            items = dataset_resp.json()

            print(f"✅ Retrieved {len(items)} items from Apify dataset")

            top_videos = []
            for item in items[:5]:
                top_videos.append({
                    "username": item.get("authorMeta", {}).get("name", "unknown"),
                    "views": item.get("stats", {}).get("playCount", "N/A"),
                    "posted": item.get("createTimeISO", "N/A")
                })

            return top_videos

        except Exception as e:
            print("❌ Exception during Apify fetch:", str(e))
            return [{"error": str(e)}]
