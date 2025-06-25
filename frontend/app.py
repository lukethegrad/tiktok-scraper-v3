import streamlit as st
import requests

st.title("🎵 TikTok Sound Analyzer")
st.markdown("Paste a TikTok sound link below to get metadata.")

sound_url = st.text_input("TikTok Sound URL:")

if sound_url:
    with st.spinner("Scraping TikTok data..."):
        try:
            # Replace this with your current ngrok tunnel URL
            ngrok_url = "https://ca5a-34-91-169-86.ngrok-free.app"
            endpoint = f"{ngrok_url}/scrape"
            response = requests.get(endpoint, params={"sound_url": sound_url})
            data = response.json()

            if "error" in data:
                st.error(f"❌ Failed to scrape: {data['error']}")
            else:
                st.success("✅ Scrape successful!")
                st.write(f"**Title:** {data['title']}")
                st.write(f"**UGC Videos:** {data['ugc_count']}")

        except Exception as e:
            st.error(f"Unexpected error: {e}")
