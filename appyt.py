import streamlit as st
import time
import yt_dlp
from downloader import download_video_or_playlist

st.set_page_config(page_title="Ravanaytdownloader", layout="centered")
st.title("Ravana YT Downloader")

# URL input and content type
col1, col2 = st.columns([3, 1])
with col1:
    url = st.text_input("Enter YouTube Video or Playlist URL")
with col2:
    content_type = st.radio("Content Type", ["Single Video", "Playlist"], horizontal=True, key="content_type")

# Preview Section
if url.strip():
    st.markdown("---")
    st.subheader("Content Preview")
    
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False  # Always get full info
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        # ------------------- PLAYLIST MODE -------------------
        if content_type == "Playlist" and 'entries' in info and info['entries']:
            playlist_title = info.get('title', 'Unknown Playlist')
            st.markdown(f"**Playlist:** {playlist_title}")
            st.markdown(f"**Total Videos:** {len(info['entries'])}")
            st.markdown("---")

            # List all videos
            for idx, entry in enumerate(info['entries'], 1):
                if not entry:
                    continue

                video_id = entry.get('id')
                title = entry.get('title', 'Unknown Title')
                channel = entry.get('uploader', 'Unknown Channel')
                duration = entry.get('duration')
                thumbnail = entry.get('thumbnail')

                duration_str = f"{duration//60}:{duration%60:02d}" if duration else "Live"

                with st.container():
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        if thumbnail:
                            st.image(thumbnail, use_column_width=True)
                        else:
                            st.caption("No thumbnail")
                    with col2:
                        st.markdown(f"**{idx}. {title}**")
                        st.caption(f"Channel: {channel} | Duration: {duration_str}")

                    # Embedded Player (Click to Play)
                    if video_id:
                        embed_url = f"https://www.youtube.com/embed/{video_id}?rel=0"
                        with st.expander(f"Play Video: {title}", expanded=False):
                            st.video(embed_url)

                    st.markdown("---")

        # ------------------- SINGLE VIDEO MODE -------------------
        else:
            # Single video
            video_id = info.get('id')
            title = info.get('title', 'Unknown Video')
            channel = info.get('uploader', 'Unknown Channel')
            duration = info.get('duration')
            thumbnail = info.get('thumbnail')
            views = info.get('view_count', 0)

            duration_str = f"{duration//60}:{duration%60:02d}" if duration else "Live"

            st.markdown(f"**Title:** {title}")
            st.markdown(f"**Channel:** {channel}")
            st.markdown(f"**Duration:** {duration_str} | **Views:** {views:,}")

            if thumbnail:
                st.image(thumbnail, use_column_width=True)
            else:
                st.info("Thumbnail not available.")

            # Embedded Player
            if video_id:
                st.markdown("### Play Video")
                st.video(f"https://www.youtube.com/embed/{video_id}?rel=0")

    except Exception as e:
        st.error(f"Failed to load content: {e}")

# Download options
st.markdown("---")
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
            for percent in range(0, 100, 10):
                time.sleep(0.2)
                progress_bar.progress(percent + 10)
                remaining = int((100 - (percent + 10)) / 10 * 0.2)
                status_text.text(f"Downloading... {percent + 10}% | Estimated time left: {remaining}s")

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
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'>Created by D.Abhiram</div>", unsafe_allow_html=True)
