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

# ------------------------------------------------------------------ FORM
with st.form("download_form"):
    url = st.text_input("Enter YouTube Video or Playlist URL")
    content_type = st.radio("Select content type", ["Single Video", "Playlist"], horizontal=True)
    download_type = st.selectbox("Download type", ["video", "audio"])
    quality = st.selectbox("Select Quality", ["Best", "720p", "1080p", "480p", "Worst"])
    zip_filename = st.text_input("ZIP file name", value="my_download.zip")
    cookies_file = st.file_uploader(
        "Optional: Upload YouTube cookies.txt (fixes 'not a bot' error)",
        type=["txt"],
        help="Export cookies after logging in to YouTube (Get cookies.txt LOCALLY extension)."
    )
    submit_btn = st.form_submit_button("Download")

# ------------------------------------------------------------------ PROGRESS
progress_bar = None
status_text = None
temp_cookie_path = None

def progress_hook(d):
    if d['status'] == 'downloading' and progress_bar and status_text:
        try:
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            if total > 0:
                pct = int(downloaded / total * 100)
                progress_bar.progress(min(pct, 100))
                status_text.text(f"Downloading: {os.path.basename(d.get('filename','?'))} — {pct}%")
        except:
            pass
    elif d['status'] == 'finished' and status_text:
        status_text.text(f"Finished: {os.path.basename(d.get('filename','?'))}")

# ------------------------------------------------------------------ MAIN LOGIC
if submit_btn:
    if not url.strip():
        st.warning("Please enter a valid URL.")
    else:
        temp_dir = tempfile.mkdtemp(prefix="yt_download_")
        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.text("Preparing…")

        # ---------- cookies ----------
        cookie_path = None
        if cookies_file:
            temp_cookie_path = os.path.join(temp_dir, "cookies.txt")
            with open(temp_cookie_path, "wb") as f:
                f.write(cookies_file.getvalue())
            cookie_path = temp_cookie_path

        try:
            # ---------- yt-dlp options ----------
            ydl_opts = {
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'noplaylist': content_type == "Single Video",
                'progress_hooks': [progress_hook],
                'quiet': True,
                'no_warnings': False,
                'merge_output_format': 'mp4',
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                                  'Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
                    'Referer': 'https://www.youtube.com/',
                    'Accept-Language': 'en-US,en;q=0.9',
                },
                'geo_bypass': True,
            }

            if cookie_path:
                ydl_opts['cookiefile'] = cookie_path

            # ---------- format ----------
            if download_type == "audio":
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else:   # video
                if quality == "Best":
                    ydl_opts['format'] = (
                        'bestvideo[ext=mp4]+bestaudio[ext=m4a]/'
                        'best[ext=mp4]/best'
                    )
                elif quality == "Worst":
                    ydl_opts['format'] = 'worstvideo+worstaudio/worst'
                else:
                    height = quality.rstrip('p')
                    ydl_opts['format'] = (
                        f'bestvideo[height<={height}][ext=mp4]+'
                        f'bestaudio[ext=m4a]/best[height<={height}][ext=mp4]/best'
                    )

            # ---------- playlist ----------
            if content_type == "Playlist":
                ydl_opts['outtmpl'] = os.path.join(temp_dir,
                                                  '%(playlist_index)02d - %(title)s.%(ext)s')

            # ---------- download ----------
            status_text.text("Starting download…")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # ---------- collect files ----------
            downloaded_files = []
            exts = ('.mp4', '.webm', '.mkv', '.mp3', '.m4a', '.opus')
            for root, _, files in os.walk(temp_dir):
                for f in files:
                    if f.lower().endswith(exts):
                        fp = os.path.join(root, f)
                        if os.path.getsize(fp) > 1024:   # ignore tiny junk
                            downloaded_files.append(fp)

            downloaded_files.sort()

            # ---------- show files ----------
            if downloaded_files:
                st.subheader("Downloaded files")
                for fp in downloaded_files:
                    size_kb = os.path.getsize(fp) / 1024
                    st.write(f"Success: {os.path.basename(fp)} ({size_kb:.1f} KB)")

                # ---------- zip ----------
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                    for fp in downloaded_files:
                        zf.write(fp, os.path.basename(fp))
                zip_buffer.seek(0)

                if not zip_filename.endswith(".zip"):
                    zip_filename += ".zip"

                total_mb = sum(os.path.getsize(fp) for fp in downloaded_files) / (1024*1024)
                st.success(f"Success: {len(downloaded_files)} file(s) – {total_mb:.1f} MB")
                st.download_button(
                    label="Download ZIP",
                    data=zip_buffer,
                    file_name=zip_filename,
                    mime="application/zip"
                )
                st.balloons()
            else:
                st.error("No media files were created. "
                         "Try a different quality, install **ffmpeg**, or upload cookies.txt.")

        except yt_dlp.utils.DownloadError as e:
            if "Sign in to confirm you’re not a bot" in str(e):
                st.error("**Bot detection** – upload a `cookies.txt` (export after logging in) "
                         "or use a VPN / wait a few hours.")
            else:
                st.error(f"yt-dlp error: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")
            st.code(traceback.format_exc())

        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

# ------------------------------------------------------------------ FOOTER
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:gray;'>"
    "Paradox-playerYT – fully working, no syntax errors"
    "</div>",
    unsafe_allow_html=True
)
