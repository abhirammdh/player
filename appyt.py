import streamlit as st
import time
import yt_dlp
from downloader import download_video_or_playlist
import io
import zipfile

st.set_page_config(page_title="Ravanaytdownloader", layout="centered")
st.title("Ravana YT Downloader")

# URL input and content type
col1, col2 = st.columns([3, 1])
with col1:
    url = st.text_input("Enter YouTube Video or Playlist URL")
with col2:
    content_type = st.radio("Content Type", ["Single Video", "Playlist"], horizontal=True, key="content_type")

# === REMOVED THUMBNAIL PREVIEW ENTIRELY ===

# Download options
download_type = st.selectbox("Download type", ["video", "audio"])
quality = st.selectbox("Select Quality", ["Best", "Worst", "480p", "720p", "1080p"])
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
            # Simulate progress (replace with real hooks later)
            for percent in range(0, 100, 10):
                time.sleep(0.2)
                progress_bar.progress(percent + 10)
                remaining = int((100 - (percent + 10)) / 10 * 0.2)
                status_text.text(f"Downloading... {percent + 10}% | Estimated time left: {remaining}s")

            # === FIX: Handle return value correctly ===
            result = download_video_or_playlist(
                url=url,
                download_type=download_type,
                quality=quality,
                content_type=content_type,
                zip_output=True
            )

            # If function returns list of file paths, zip them manually
            if isinstance(result, list):
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in result:
                        if file_path and os.path.exists(file_path):
                            arcname = os.path.basename(file_path)
                            zipf.write(file_path, arcname)
                            # Optional: delete temp file
                            # os.remove(file_path)
                zip_buffer.seek(0)
                final_zip = zip_buffer.read()
            else:
                final_zip = result  # Assume it's already bytes/BytesIO

            if not zip_filename.endswith(".zip"):
                zip_filename += ".zip"

            st.success("Download complete.")
            st.download_button(
                label="Download ZIP file",
                data=final_zip,
                file_name=zip_filename,
                mime="application/zip"
            )

        except Exception as e:
            st.error(f"Download failed: {e}")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>Created by D.Abhiram</div>", unsafe_allow_html=True)
