import asyncio
from flask import Flask, request, jsonify
from scraper import scrape_tiktok_sound_async

app = Flask(__name__)

@app.route("/scrape", methods=["GET"])
def scrape_route():
    sound_url = request.args.get("sound_url")
    if not sound_url:
        return jsonify({"error": "Missing sound_url parameter"}), 400

    try:
        result = asyncio.run(scrape_tiktok_sound_async(sound_url))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
