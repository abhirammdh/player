import streamlit as st
import yt_dlp
import os

st.set_page_config(page_title="YouTube Downloader", layout="centered")
st.title("🎥 YouTube Video Downloader (yt-dlp)")

st.write("Paste one or multiple YouTube URLs below (each URL on a new line).")

# URL input (multi-line)
urls_text = st.text_area("YouTube URLs", height=150, placeholder="https://youtu.be/abc\nhttps://youtube.com/xyz")

# Folder name input
folder_name = st.text_input("Folder name to save videos", "downloads")

# Download button
if st.button("Download Videos"):
    if urls_text.strip() == "":
        st.error("Please enter at least one YouTube URL.")
    else:
        video_urls = urls_text.splitlines()
        save_path = folder_name.strip()

        # Create folder if not exists
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        # YDL Options
        ydl_opts = {
            "format": "best",  
            "outtmpl": f"{save_path}/%(title)s.%(ext)s",
        }

        st.info("Downloading... please wait.")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download(video_urls)
                st.success("✅ Download Completed!")
            except Exception as e:
                st.error(f"❌ Error: {e}")
