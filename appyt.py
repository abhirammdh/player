import streamlit as st
import time
import random
import yt_dlp
from downloader import download_video_or_playlist   # <-- your own helper

# ------------------------------------------------------------
# Page config
# ------------------------------------------------------------
st.set_page_config(page_title="Ravanaytdownloader", layout="centered")
st.title("Ravana YT Downloader")

# ------------------------------------------------------------
# URL input + content type
# ------------------------------------------------------------
col1, col2 = st.columns([3, 1])
with col1:
    url = st.text_input("Enter YouTube Video or Playlist URL")
with col2:
    content_type = st.radio(
        "Content Type", ["Single Video", "Playlist"], horizontal=True, key="content_type"
    )

# ------------------------------------------------------------
# Helper: extract info with realistic headers + retries
# ------------------------------------------------------------
def extract_info(url: str, is_playlist: bool):
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": "in_playlist" if is_playlist else False,
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/128.0.0.0 Safari/537.36"
            ),
            "Referer": "https://www.youtube.com/",
            "Accept-Language": "en-US,en;q=0.9",
        },
        # "cookiefile": "cookies.txt",   # <-- uncomment & add a cookies.txt if needed
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)
        except Exception:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt + random.random())   # exponential back-off

    return None


# ------------------------------------------------------------
# Preview section
# ------------------------------------------------------------
if url.strip():
    st.markdown("---")
    st.subheader("Content Preview")

    try:
        info = extract_info(url, content_type == "Playlist")
        if not info:
            st.warning("Could not retrieve info after several attempts.")
        else:
            # ---------- Playlist ----------
            if content_type == "Playlist" and "entries" in info and info["entries"]:
                playlist_title = info.get("title", "Unknown Playlist")
                first = next((e for e in info["entries"] if e), {})
                channel = first.get("uploader", "Unknown Channel")
                thumbnail = first.get("thumbnail")
                video_cnt = len([e for e in info["entries"] if e])

                st.markdown(f"**Playlist:** {playlist_title}")
                st.markdown(f"**Channel:** {channel}")
                st.markdown(f"**Videos:** {video_cnt}")
            # ---------- Single video ----------
            else:
                title = info.get("title", "Unknown Video")
                channel = info.get("uploader", "Unknown Channel")
                thumbnail = info.get("thumbnail")

                st.markdown(f"**Title:** {title}")
                st.markdown(f"**Channel:** {channel}")

            # Thumbnail
            if thumbnail:
                st.image(thumbnail, use_column_width=True)
            else:
                st.info("Thumbnail not available.")
    except Exception as e:
        st.warning(f"Could not fetch details: {e}")

# ------------------------------------------------------------
# Download options
# ------------------------------------------------------------
st.markdown("---")
download_type = st.selectbox("Download type", ["video", "audio"])
quality = st.selectbox("Select Quality", ["Best", "Worst", "480p", "720p", "1080p"])
zip_filename = st.text_input("ZIP file name", value="my_download.zip")

# ------------------------------------------------------------
# Download button
# ------------------------------------------------------------
if st.button("Download"):
    if not url.strip():
        st.warning("Please enter a valid URL.")
    else:
        st.info("Download started. Please wait...")
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # ---- Simulated progress (remove time.sleep in production) ----
            for percent in range(0, 100, 10):
                time.sleep(0.2)                     # <-- demo only
                progress_bar.progress(percent + 10)
                remaining = int((100 - (percent + 10)) / 10 * 0.2)
                status_text.text(
                    f"Downloading... {percent + 10}% | "
                    f"Estimated time left: {remaining}s"
                )

            # ---- Real download ----
            zip_buffer = download_video_or_playlist(
                url=url,
                download_type=download_type,
                quality=quality,
                content_type=content_type,
                zip_output=True,
            )

            if not zip_filename.lower().endswith(".zip"):
                zip_filename += ".zip"

            st.success("Download complete.")
            st.download_button(
                label="Download ZIP file",
                data=zip_buffer,
                file_name=zip_filename,
                mime="application/zip",
            )
        except Exception as e:
            st.error(f"Download failed: {e}")

# ------------------------------------------------------------
# Footer
# ------------------------------------------------------------
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>Created by D.Abhiram</div>",
    unsafe_allow_html=True,
)

