import streamlit as st
import time
import yt_dlp
from downloader import download_video_or_playlist

st.set_page_config(page_title="Ravanaytdownloader", layout="centered")
st.title("Ravana yt downloader")

# URL input and thumbnail preview
col1, col2 = st.columns([3, 1])

with col1:
    url = st.text_input("Enter YouTube Video or Playlist URL")

with col2:
    content_type = st.radio("Content Type", ["Single Video", "Playlist"], horizontal=True, key="content_type")

# Preview Section
if url.strip():
    st.subheader("Preview")
    try:
        ydl_opts = {'quiet': True, 'no_warnings': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # Detect thumbnail (video or playlist)
            thumb = None
            if 'entries' in info and info['entries'] and info['entries'][0]:
                entry = info['entries'][0]
                thumb = entry.get('thumbnail')
            else:
                thumb = info.get('thumbnail')

            if thumb:
                st.image(thumb, caption="Thumbnail Preview", use_column_width=True)
            else:
                st.info("Thumbnail not available.")
    except Exception as e:
        st.warning(f"Could not fetch thumbnail: {e}")

# Other Inputs
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
            # Fake progress animation
            for percent in range(0, 100, 10):
                time.sleep(0.2)
                progress_bar.progress(percent + 10)
                elapsed = time.time() - start_time
                remaining = int((100 - percent) / 10 * 0.2)
                status_text.text(
                    f"Downloading... {percent + 10}% | Estimated time left: {remaining}s"
                )

            # Actual download call
            zip_buffer = download_video_or_playlist(
                url=url,
                download_type=download_type,
                quality=quality,
                content_type=content_type,
                zip_output=True
            )

            if not zip_filename.endswith(".zip"):
                zip_filename += ".zip"

            st.success("Download complete.")

            st.download_button(
                label="Download ZIP file",
                data=zip_buffer,
                file_name=zip_filename,
                mime="application/zip"
            )

        except Exception as e:
            st.error(f"Download failed: {e}")

# Footer
st.markdown("""---""")
st.markdown(
    "<div style='text-align: center; color: gray;'>Created by D. Abhiram</div>",
    unsafe_allow_html=True
)
