import streamlit as st
import requests

st.title("🎵 TikTok Sound Analyzer")
st.markdown("Paste a TikTok sound link below to get metadata.")

sound_url = st.text_input("TikTok Sound URL:")

if sound_url:
    with st.spinner("Scraping TikTok data..."):
        try:
            backend_url = "https://backend-quiet-wave-4398.fly.dev"
            endpoint = f"{backend_url}/scrape"
            response = requests.get(endpoint, params={"sound_url": sound_url})
            data = response.json()

            if "error" in data:
                st.error(f"❌ Failed to scrape: {data['error']}")
            else:
                st.success("✅ Scrape successful!")
                st.write(f"**Title:** {data['title']}")
                st.write(f"**UGC Videos:** {data['ugc_count']}")
                st.write(f"**Total Views (estimated):** {data['total_views']}")

                # 🔥 Top 5 videos
                if "top_videos" in data and data["top_videos"]:
                    st.markdown("### 🔝 Top 5 Videos")
                    for i, video in enumerate(data["top_videos"], start=1):
                        st.markdown(f"""
                            **#{i}**
                            - 👤 **User:** {video['username']}
                            - 👁️ **Views:** {video['views']}
                            - 📅 **Posted:** {video['post_date']}
                        """)
                else:
                    st.warning("⚠️ No top videos found.")

        except Exception as e:
            st.error(f"Unexpected error: {e}")

