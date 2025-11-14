import streamlit as st
import time
import yt_dlp
from downloader import download_video_or_playlist

st.set_page_config(page_title="Ravanaytdownloader", layout="centered")
st.title("🔥 Ravana YT Downloader")

# URL input and content type
col1, col2 = st.columns([3, 1])
with col1:
    url = st.text_input("Enter YouTube Video or Playlist URL")
with col2:
    content_type = st.radio("Content Type", ["Single Video", "Playlist"], horizontal=True, key="content_type")

# Preview Section
if url.strip():
    st.subheader("📺 Preview")
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            # Handle playlist or single video
            if 'entries' in info and info['entries']:
                # Playlist
                entry = info['entries'][0]  # Take first video for preview
                title = info.get('title', 'Unknown Playlist')
                thumbnail = entry.get('thumbnail')
                channel = entry.get('uploader', 'Unknown Channel')
                video_count = len(info['entries'])
                st.markdown(f"**Playlist:** {title}")
                st.markdown(f"**Channel:** {channel}")
                st.markdown(f"**Videos in Playlist:** {video_count}")
            else:
                # Single video
                title = info.get('title', 'Unknown Video')
                thumbnail = info.get('thumbnail')
                channel = info.get('uploader', 'Unknown Channel')
                duration = info.get('duration')
                duration_str = f"{duration // 60}:{duration % 60:02d}" if duration else "N/A"
                st.markdown(f"**Title:** {title}")
                st.markdown(f"**Channel:** {channel}")
                st.markdown(f"**Duration:** {duration_str}")

            # Show thumbnail
            if thumbnail:
                st.image(thumbnail, caption="Thumbnail Preview", use_column_width=True)
            else:
                st.info("Thumbnail not available.")

    except Exception as e:
        st.warning(f"Could not fetch info: {e}")

# Download Options
st.markdown("---")
download_type = st.selectbox("Download Type", ["video", "audio"])
quality = st.selectbox("Select Quality", ["Best", "Worst", "480p", "720p", "1080p"])
zip_filename = st.text_input("ZIP File Name", value="my_download.zip")

# Download Button
submit_btn = st.button("🚀 Download", type="primary")

if submit_btn:
    if not url.strip():
        st.warning("Please enter a valid URL.")
    else:
        st.info("Download started. Please wait...")
        progress_bar = st.progress(0)
        status_text = st.empty()
        start_time = time.time()

        try:
            # Simulate progress (replace with real progress in downloader if possible)
            for percent in range(0, 100, 10):
                time.sleep(0.2)
                progress_bar.progress(percent + 10)
                elapsed = time.time() - start_time
                remaining = int((100 - (percent + 10)) / 10 * 0.2)
                status_text.text(f"Downloading... {percent + 10}% | Estimated time left: {remaining}s")

            # Actual download
            zip_buffer = download_video_or_playlist(
                url=url,
                download_type=download_type,
                quality=quality,
                content_type=content_type,
                zip_output=True
            )

            if not zip_filename.endswith(".zip"):
                zip_filename += ".zip"

            st.success("Download complete! 🎉")
            st.download_button(
                label="📥 Download ZIP File",
                data=zip_buffer,
                file_name=zip_filename,
                mime="application/zip"
            )
        except Exception as e:
            st.error(f"Download failed: {e}")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>Created with ❤️ by D.Abhiram</div>",
    unsafe_allow_html=True
)
