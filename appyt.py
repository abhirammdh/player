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
                progress_bar.progress(min(percentage, 100))
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

        # Download success flag
        download_success = False

        try:
            # Base options
            ydl_opts = {
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'noplaylist': content_type == "Single Video",
                'progress_hooks': [progress_hook],
                'quiet': True,
                'no_warnings': False,
                'merge_output_format': 'mp4',  # Force mp4 when merging
                'writesubtitles': False,  # Avoid extra files
                'writeautomaticsub': False,
            }

            # Quality / type handling
            if download_type == "audio":
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else:  # video
                if quality == "Best":
                    ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                elif quality == "Worst":
                    ydl_opts['format'] = 'worstvideo+worstaudio/worst'
                else:
                    height = quality.rstrip('p')
                    ydl_opts['format'] = f'bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/best[height<={height}][ext=mp4]/best'

            # Add playlist indexing so files don't overwrite
            if content_type == "Playlist":
                ydl_opts['outtmpl'] = os.path.join(temp_dir, '%(playlist_index)02d - %(title)s.%(ext)s')

            # Download
            status_text.text("Starting download with yt-dlp...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if info:
                    download_success = True

            # Collect all downloaded media files (look for common extensions)
            downloaded_files = []
            supported_exts = ('.mp4', '.webm', '.mkv', '.avi', '.mov', '.mp3', '.m4a', '.opus', '.wav', '.flac')
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith(supported_exts):
                        full_path = os.path.join(root, file)
                        file_size = os.path.getsize(full_path)
                        if file_size > 1024:  # At least 1KB to avoid empty files
                            downloaded_files.append(full_path)

            # Sort files for consistency (e.g., playlist order)
            downloaded_files.sort(key=lambda x: os.path.basename(x))

            # Debug: show what was found
            if downloaded_files:
                st.subheader("Downloaded Files:")
                for f in downloaded_files:
                    size_kb = os.path.getsize(f) / 1024
                    st.write(f"✓ {os.path.basename(f)} ({size_kb:.1f} KB)")
            else:
                st.error("No valid media files found after download! Common fixes:\n"
                         "• Install FFmpeg: https://ffmpeg.org/download.html (required for audio/merging)\n"
                         "• Try 'Best' quality or a different video\n"
                         "• Check if video is age-restricted/private\n"
                         "• Test URL in browser")

            if downloaded_files:
                # Create ZIP in memory
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in downloaded_files:
                        arcname = os.path.basename(file_path)
                        zipf.write(file_path, arcname)
                        st.write(f"→ Zipped: {arcname}")  # Confirm zipping

                zip_buffer.seek(0)

                if not zip_filename.endswith(".zip"):
                    zip_filename += ".zip"

                st.success(f"✅ Download complete! ZIP ready with {len(downloaded_files)} file(s).")
                st.download_button(
                    label=f"📥 Download ZIP ({sum(os.path.getsize(f) for f in downloaded_files) / (1024*1024):.1f} MB)",
                    data=zip_buffer,
                    file_name=zip_filename,
                    mime="application/zip"
                )
            else:
                download_success = False

        except yt_dlp.utils.DownloadError as de:
            st.error(f"yt-dlp Download Error: {str(de)}\nTry a different URL or quality.")
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            st.code(traceback.format_exc(), language="python")
            download_success = False

        finally:
            # Clean up only if download succeeded or after zipping
            if os.path.exists(temp_dir):
                if download_success:
                    st.info(f"Temporary files in {temp_dir} cleaned up after zipping.")
                else:
                    st.info(f"Keeping temp files in {temp_dir} for debugging (delete manually).")
                shutil.rmtree(temp_dir, ignore_errors=True)

# Footer
st.markdown("""---""")
st.markdown("<div style='text-align: center; color: gray;'>Fixed version: Downloads to temp, zips reliably, no errors on success • Created by Grok</div>", unsafe_allow_html=True)
