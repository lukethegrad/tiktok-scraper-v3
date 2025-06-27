from flask import Flask, request, jsonify
from scraper import scrape_tiktok_sound
from apify_fetcher import fetch_top_videos_from_apify
import asyncio

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        data = request.get_json()
        sound_url = data.get("sound_url")

        if not sound_url:
            return jsonify({"error": "Missing 'sound_url' in request"}), 400

        # 🎵 Get title + UGC from Playwright
        scraped_data = scrape_tiktok_sound(sound_url)
        if not scraped_data or scraped_data.get("title") == "Error":
            return jsonify({"error": "Scraper failed", "details": scraped_data}), 500

        # 🎥 Get top videos from Apify
        top_videos = asyncio.run(fetch_top_videos_from_apify(sound_url))

        response = {
            "sound_title": scraped_data["title"],
            "ugc_count": scraped_data["ugc_count"],
            "top_videos": top_videos
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
