import streamlit as st
import yt_dlp
import os
import tempfile

st.set_page_config(page_title="YouTube Downloader", layout="centered")
st.title("🎥 YouTube Downloader (yt-dlp with Cookies)")


st.write("Paste YouTube URLs (each URL on a new line):")
urls_text = st.text_area("YouTube URLs", height=150)

folder_name = st.text_input("Folder name to save videos", "downloads")

# Upload cookies file
cookies_file = st.file_uploader("Upload cookies.txt file (from your browser)", type=["txt"])


if st.button("Download"):
    if urls_text.strip() == "":
        st.error("Please enter URLs.")
    else:
        video_urls = urls_text.splitlines()

        # Create output folder
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        # Save uploaded cookies to temp file
        cookies_path = None
        if cookies_file is not None:
            temp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
            temp.write(cookies_file.read())
            temp.close()
            cookies_path = temp.name
        
        # yt-dlp options
        ydl_opts = {
            "format": "best",
            "outtmpl": f"{folder_name}/%(title)s.%(ext)s",
        }

        if cookies_path:
            ydl_opts["cookiefile"] = cookies_path

        st.info("Downloading... please wait")

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(video_urls)

            st.success("✅ Download completed!")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

