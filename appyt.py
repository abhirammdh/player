import streamlit as st
import os
import zipfile
import tempfile
import shutil
import traceback
from io import BytesIO
import yt_dlp

st.set_page_config(page_title="Paradox-Player", layout="centered")
st.title("Paradox-playerYT Downloader")

# Form
with st.form("download_form"):
    url = st.text_input("Enter YouTube Video or Playlist URL")
    content_type = st.radio("Select content type", ["Single Video", "Playlist"], horizontal=True)
    download_type = st.selectbox("Download type", ["video", "audio"])
    quality = st.selectbox("Select Quality", ["Best", "Worst", "480p", "720p", "1080p"])
    zip_filename = st.text_input("ZIP file name", value="my_download.zip")
    submit_btn = st.form_submit_button("Download")

# Progress placeholders (will be reused)
progress_bar = None
status_text = None

def progress_hook(d):
    if d['status'] == 'downloading' and progress_bar and status_text:
        try:
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                percentage = int(downloaded / total * 100)
                progress_bar.progress(percentage)
                status_text.text(f"Downloading: {os.path.basename(d.get('filename', 'unknown'))} — {percentage}%")
        except:
            pass
    elif d['status'] == 'finished' and status_text:
        status_text.text(f"Finished: {os.path.basename(d.get('filename', 'unknown'))}")

if submit_btn:
    if not url.strip():
        st.warning("Please enter a valid URL.")
    else:
        # Create unique temp folder for this download
        temp_dir = tempfile.mkdtemp(prefix="yt_download_")
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.text("Preparing download...")

        try:
            # Base options
            ydl_opts = {
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'noplaylist': content_type == "Single Video",
                'progress_hooks': [progress_hook],
                'quiet': True,
                'no_warnings': False,
                'merge_output_format': 'mp4',  # Force mp4 when merging
            }

            # Quality / type handling
            if download_type == "audio":
                ydl_opts['format'] = 'bestaudio'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else:  # video
                if quality == "Best":
                    ydl_opts['format'] = 'bv*+ba/b'  # best video + audio, fallback to best single file
                elif quality == "Worst":
                    ydl_opts['format'] = 'wv*+wa/w'
                else:
                    height = quality.rstrip('p')
                    ydl_opts['format'] = f'(bv*[height<={height}]+ba/b)[ext=mp4]/best[height<={height}]'

            # Add playlist indexing so files don't overwrite less
            if content_type == "Playlist":
                ydl_opts['outtmpl'] = os.path.join(temp_dir, '%(playlist_index)02d - %(title)s.%(ext)s')

            # Download
            status_text.text("Starting download with yt-dlp...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # Collect all downloaded media files
            downloaded_files = []
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith(('.mp4', '.webm', '.mkv', '.mp3', '.m4a', '.opus', '.aac')):
                        full_path = os.path.join(root, file)
                        if os.path.getsize(full_path) > 0:
                            downloaded_files.append(full_path)

            # Debug: show what was found
            st.write(f"Found {len(downloaded_files)} file(s) in temp folder:")
            for f in downloaded_files:
                st.write(f"✓ {os.path.basename(f)} ({os.path.getsize(f) / 1024:.1f} KB)")

            if not downloaded_files:
                st.error("No files were downloaded! Possible reasons:\n"
                         "- Invalid or private/age-restricted video\n"
                         "- Selected quality not available\n"
                         "- ffmpeg missing (required for audio or high-quality merging)\n"
                         "- Network / YouTube blocking the request")
            else:
                # Create ZIP in memory
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in downloaded_files:
                        zipf.write(file_path, os.path.basename(file_path))
                zip_buffer.seek(0)

                if not zip_filename.endswith(".zip"):
                    zip_filename += ".zip"

                st.success(f"Success! {len(downloaded_files)} file(s) ready for download.")
                st.download_button(
                    label="📥 Download ZIP file",
                    data=zip_buffer,
                    file_name=zip_filename,
                    mime="application/zip"
                )

        except Exception as e:
            st.error(f"Download failed: {str(e)}")
            st.code(traceback.format_exc())

        finally:
            # Always clean up temp files
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                st.info("Temporary files cleaned up.")

# Footer
st.markdown("""---""")
st.markdown("<div style='text-align: center; color: gray;'>Fixed & improved version using yt-dlp directly • Created by Grok for you</div>", unsafe_allow_html=True)
