import streamlit as st
import yt_dlp
import zipfile
from io import BytesIO
import os
import tempfile
import shutil
from typing import List, Dict, Any

# ----------------------------------------------------------------------
# Helper: extract info + thumbnails for a video/playlist
# ----------------------------------------------------------------------
def get_info_and_thumbs(url: str) -> List[Dict[str, Any]]:
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,          # we need full info
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    entries = []
    if "entries" in info:                     # playlist
        for e in info["entries"]:
            if e:
                entries.append(e)
    else:                                     # single video
        entries.append(info)

    # Attach thumbnail URL (yt-dlp already gives the best one)
    for e in entries:
        e["thumb_url"] = e.get("thumbnail") or e.get("thumbnails", [{}])[-1].get("url")

    return entries

# ----------------------------------------------------------------------
# Helper: download ONE entry (video or audio) + optional thumbnail
# ----------------------------------------------------------------------
def download_entry(
    entry: Dict[str, Any],
    download_type: str,
    quality: str,
    tmp_dir: str,
) -> str:
    """
    Returns the path of the downloaded file inside tmp_dir.
    """
    vid_id = entry["id"]
    out_dir = os.path.join(tmp_dir, vid_id)
    os.makedirs(out_dir, exist_ok=True)

    # ---------- yt-dlp format selector ----------
    if download_type == "video":
        if quality == "Best":
            fmt = "bestvideo+bestaudio/best"
        elif quality == "Worst":
            fmt = "worstvideo+worsstaudio/worst"
        else:
            fmt = f"bestvideo[height<={quality[:-1]}]+bestaudio/best"
    else:  # audio
        fmt = "bestaudio"

    ydl_opts = {
        "format": fmt,
        "outtmpl": os.path.join(out_dir, "%(title)s.%(ext)s"),
        "merge_output_format": "mp4" if download_type == "video" else None,
        "writethumbnail": True,                 # saves .jpg/.webp
        "skip_download": False,
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([entry["original_url"]])

    # Find the downloaded media file
    for f in os.listdir(out_dir):
        if not f.endswith((".jpg", ".webp", ".png")):   # skip thumbnail files
            return os.path.join(out_dir, f)

    raise RuntimeError("No media file found after download")

# ----------------------------------------------------------------------
# Page layout
# ----------------------------------------------------------------------
st.set_page_config(page_title="RavanaYTDownloader", layout="centered")
st.title("🎥 Ravana YT Downloader")

col1, col2 = st.columns([3, 1])
with col1:
    url = st.text_input("Enter YouTube Video or Playlist URL")
with col2:
    content_type = st.radio(
        "Content Type", ["Single Video", "Playlist"], horizontal=True, key="content_type"
    )

download_type = st.selectbox("Download type", ["video", "audio"])
quality = st.selectbox("Select Quality", ["Best", "Worst", "480p", "720p", "1080p"])
zip_filename = st.text_input("ZIP file name", value="my_download.zip")

# ----------------------------------------------------------------------
# 1. Show ALL thumbnails
# ----------------------------------------------------------------------
thumbs_container = st.container()
if url.strip():
    with st.spinner("Fetching thumbnails…"):
        try:
            entries = get_info_and_thumbs(url)
        except Exception as e:
            st.error(f"Could not fetch info: {e}")
            entries = []

    if entries:
        with thumbs_container:
            st.subheader(f"Preview – {len(entries)} item(s)")
            cols = st.columns(4)               # change number to fit your screen
            for idx, entry in enumerate(entries):
                thumb = entry.get("thumb_url")
                title = entry.get("title", "Untitled")
                with cols[idx % 4]:
                    if thumb:
                        st.image(thumb, caption=title, use_column_width=True)
                    else:
                        st.caption(f"**{title}** – *no thumbnail*")
    else:
        thumbs_container.info("Enter a valid URL to see thumbnails.")

# ----------------------------------------------------------------------
# 2. Download button
# ----------------------------------------------------------------------
if st.button("🚀 Download"):
    if not url.strip():
        st.warning("Please enter a URL.")
    else:
        # ---------- progress UI ----------
        progress_bar = st.progress(0)
        status_text = st.empty()

        # ---------- temporary workspace ----------
        tmp_base = tempfile.mkdtemp()
        zip_buffer = BytesIO()

        try:
            entries = get_info_and_thumbs(url)          # reuse same call
            total = len(entries)

            for i, entry in enumerate(entries):
                percent = int((i + 1) / total * 100)
                progress_bar.progress(percent)
                status_text.text(
                    f"Downloading **{entry.get('title','…')}** ({i+1}/{total}) – {percent}%"
                )

                # download media + thumbnail
                media_path = download_entry(entry, download_type, quality, tmp_base)

                # rename thumbnail to a predictable name (cover.jpg)
                vid_dir = os.path.dirname(media_path)
                for ext in (".jpg", ".webp", ".png"):
                    possible = os.path.join(vid_dir, os.path.basename(media_path).rsplit(".", 1)[0] + ext)
                    if os.path.exists(possible):
                        shutil.copy(possible, os.path.join(vid_dir, "cover.jpg"))
                        break

            # ---------- create ZIP ----------
            status_text.text("Creating ZIP file…")
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(tmp_base):
                    for f in files:
                        full_path = os.path.join(root, f)
                        # store with relative path inside ZIP
                        arcname = os.path.relpath(full_path, tmp_base)
                        zf.write(full_path, arcname)

            zip_buffer.seek(0)
            if not zip_filename.lower().endswith(".zip"):
                zip_filename += ".zip"

            st.success("✅ All files downloaded & zipped!")
            st.download_button(
                label="📦 Download ZIP",
                data=zip_buffer,
                file_name=zip_filename,
                mime="application/zip",
            )

        except Exception as exc:
            st.error(f"Download failed: {exc}")
        finally:
            # clean temporary folder
            shutil.rmtree(tmp_base, ignore_errors=True)
            progress_bar.empty()
            status_text.empty()

# ----------------------------------------------------------------------
# Footer
# ----------------------------------------------------------------------
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>Created by D.Abhiram – "
    "<a href='https://github.com/abhiram-d'>GitHub</a></div>",
    unsafe_allow_html=True,
)
