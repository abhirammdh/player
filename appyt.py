import streamlit as st
import time
from downloader import download_video_or_playlist

st.set_page_config(page_title="Paradox-Player", layout="centered")
st.title("Paradox-player YT Downloader")

# Form layout for user inputs
with st.form("download_form"):
    url = st.text_input("Enter YouTube Video or Playlist URL")
    content_type = st.radio("Select content type", ["Single Video", "Playlist"], horizontal=True)
    download_type = st.selectbox("Download type", ["video", "audio"])
    quality = st.selectbox("Select Quality", ["Best", "Worst", "480p", "720p", "1080p"])
    zip_filename = st.text_input("ZIP file name", value="my_download.zip")
    
    submit_btn = st.form_submit_button("Download")

if submit_btn:
    if not url.strip():
        st.warning("Please enter a valid URL.")
    else:
        st.info("Download started. Please wait...")
        progress_bar = st.progress(0)
        status_text = st.empty()

        start_time = time.time()

        try:
            # Fake progress simulation
            for percent in range(0, 100, 10):
                time.sleep(0.2)
                progress_bar.progress(percent + 10)
                remaining = int((100 - percent) / 10 * 0.2)
                status_text.text(f"Downloading... {percent + 10}% | Estimated time left: {remaining}s")

            # Call downloader
            zip_buffer = download_video_or_playlist(
                url=url,
                download_type=download_type,
                quality=quality,
                content_type=content_type,
                zip_output=True
            )

            # Ensure .zip extension
            if not zip_filename.endswith(".zip"):
                zip_filename += ".zip"

            st.success("Download complete!")

            st.download_button(
                label="Download ZIP file",
                data=zip_buffer,
                file_name=zip_filename,
                mime="application/zip"
            )

        except Exception as e:
            st.error(f"Download failed: {e}")

# Footer Section
st.markdown("""---""")
st.markdown(
    "<div style='text-align: center; color: gray;'>Created by Sree</div>",
    unsafe_allow_html=True
)
