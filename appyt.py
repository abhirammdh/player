import streamlit as st
import time
from downloader import download_video_or_playlist

st.set_page_config(page_title="Ravanaytdownloader", layout="centered")
st.title("Ravana YT Downloader")

# URL input and content type
col1, col2 = st.columns([3, 1])
with col1:
    url = st.text_input("Enter YouTube Video or Playlist URL")
with col2:
    content_type = st.radio("Content Type", ["Single Video", "Playlist"], horizontal=True, key="content_type")

# Download options
download_type = st.selectbox("Download type", ["video", "audio"])
quality = st.selectbox("Select Quality", ["Best", "1080p", "720p", "480p", "Worst"])
zip_filename = st.text_input("ZIP file name", value="my_download.zip")

# Download button
submit_btn = st.button("Download")

if submit_btn:
    if not url.strip():
        st.warning("Please enter a valid URL.")
    else:
        st.info("Download started. Please wait...")
        progress_bar = st.progress(0)
        status_text = st.empty()
        start_time = time.time()

        try:
            # Simulate progress (yt-dlp is fast, but this shows UI feedback)
            for percent in range(0, 100, 10):
                time.sleep(0.1)  # Shorter for realism
                progress_bar.progress(percent + 10)
                remaining = int((100 - (percent + 10)) / 10 * 0.1)
                status_text.text(f"Downloading... {percent + 10}% | Estimated time left: {remaining}s")

            # Download and get ZIP bytes
            zip_buffer = download_video_or_playlist(
                url=url,
                download_type=download_type,
                quality=quality,
                content_type=content_type,
                zip_output=True
            )

            if not zip_filename.endswith(".zip"):
                zip_filename += ".zip"

            st.success("Download complete! Files inside ZIP:")
            # List files in ZIP for verification
            with zipfile.ZipFile(io.BytesIO(zip_buffer)) as zf:
                for file in zf.namelist():
                    st.write(f"• {file}")

            st.download_button(
                label="Download ZIP file",
                data=zip_buffer,
                file_name=zip_filename,
                mime="application/zip"
            )

        except Exception as e:
            st.error(f"Download failed: {e}")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>Created by D.Abhiram</div>", unsafe_allow_html=True)
