import streamlit as st
import yt_dlp
from io import BytesIO
import time
import zipfile
import os
import tempfile
from downloader import download_video_or_playlist

# -------------------------- Page Configuration --------------------------
st.set_page_config(
    page_title="Ravana YT Downloader",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------- Custom Professional CSS --------------------------
st.markdown("""
<style>
    .main-title {
        font-size: 48px;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(90deg, #1a1a1a, #333333);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 8px;
        letter-spacing: -1px;
    }
    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #666;
        margin-bottom: 40px;
        font-weight: 400;
    }
    .preview-card {
        background-color: #ffffff;
        padding: 28px;
        border-radius: 16px;
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.08);
        border: 1px solid #e8e8e8;
        margin-bottom: 20px;
    }
    .info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 16px;
        margin: 16px 0;
        font-size: 14px;
        color: #444;
    }
    .info-item {
        background-color: #f8f9fa;
        padding: 10px 14px;
        border-radius: 10px;
        border-left: 3px solid #007bff;
    }
    .info-label {
        font-weight: 600;
        color: #2c3e50;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .info-value {
        margin-top: 4px;
        font-weight: 500;
        color: #1a1a1a;
    }
    .download-button {
        background: linear-gradient(135deg, #007bff, #0056b3);
        color: white;
        font-weight: 600;
        font-size: 18px;
        height: 56px;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
        transition: all 0.3s ease;
    }
    .download-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 123, 255, 0.4);
    }
    .stButton > button {
        border-radius: 12px !important;
    }
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 1px solid #ddd;
        padding: 12px 16px;
        font-size: 16px;
    }
    .stSelectbox > div > div > select {
        border-radius: 12px;
    }
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #e0e0e0;
    }
    .sidebar-title {
        font-size: 20px;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 20px;
        padding-bottom: 12px;
        border-bottom: 1px solid #e0e0e0;
    }
    .footer {
        text-align: center;
        padding: 30px 0;
        color: #888;
        font-size: 14px;
        border-top: 1px solid #eee;
        margin-top: 50px;
    }
    .stProgress > div > div > div > div {
        background-color: #007bff;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------- Header --------------------------
st.markdown('<div class="main-title">Ravana YT Downloader</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Professional YouTube Video & Playlist Downloader • High Quality • Fast & Reliable</div>', unsafe_allow_html=True)

# -------------------------- Sidebar Configuration --------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-title">Configuration</div>', unsafe_allow_html=True)
    
    # Theme toggle
    theme = st.selectbox("Interface Theme", ["Light", "Dark"], index=0)
    if theme == "Dark":
        st.markdown("""
        <style>
            .stApp {background-color: #121212; color: #e0e0e0;}
            .preview-card {background-color: #1e1e1e; border: 1px solid #333; color: #e0e0e0;}
            .info-item {background-color: #2d2d2d; border-left-color: #4a90e2;}
            .info-label {color: #aaa;}
            .info-value {color: #fff;}
            section[data-testid="stSidebar"] {background-color: #1a1a1a; border-right: 1px solid #333;}
            .stTextInput > div > div > input {background-color: #2d2d2d; color: #fff; border: 1px solid #444;}
            .subtitle {color: #aaa;}
            .footer {color: #777; border-top: 1px solid #333;}
        </style>
        """, unsafe_allow_html=True)

    download_type = st.radio("Download Format", ["Video", "Audio"], horizontal=True)
    
    if download_type == "Video":
        quality = st.selectbox("Video Quality", 
            ["Best Available", "1080p", "720p", "480p", "360p", "Lowest"],
            index=0)
    else:
        quality = st.selectbox("Audio Quality", 
            ["Best (Opus)", "Best (M4A)", "MP3 320kbps", "MP3 128kbps", "Lowest"],
            index=0)
    
    zip_filename = st.text_input("Archive Name", value="ravana_download.zip", help="Name of the output ZIP file")
    
    st.markdown("---")
    st.markdown("**Supported:**")
    st.caption("• Single videos\n• Full playlists\n• Shorts & Live archives\n• Age-restricted content")

# -------------------------- Main Content Area --------------------------
url = st.text_input(
    "Enter YouTube URL",
    placeholder="https://www.youtube.com/watch?v=...",
    label_visibility="collapsed"
)

info = None
is_playlist = False
content_type = "Single Video"

if url.strip():
    with st.spinner("Analyzing URL and fetching metadata..."):
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            # Detect playlist
            if info.get('_type') == 'playlist' or ('entries' in info and info['entries']):
                is_playlist = True
                content_type = "Playlist"

            # Extract metadata
            title = info.get('title', 'Unknown Title')
            thumbnail = info.get('thumbnail')
            if not thumbnail and info.get('thumbnails'):
                thumbnail = info['thumbnails'][-1]['url']
            if not thumbnail and is_playlist and info.get('entries') and info['entries']:
                first_entry = info['entries'][0]
                thumbnail = first_entry.get('thumbnail')

            # Preview Card
            with st.container():
                st.markdown('<div class="preview-card">', unsafe_allow_html=True)
                
                if is_playlist:
                    video_count = len(info.get('entries', []))
                    st.markdown(f"### Playlist: {title}")
                    st.markdown(f"**Total videos:** {video_count}")
                else:
                    uploader = info.get('uploader', 'Unknown Channel')
                    duration = info.get('duration', 0)
                    views = info.get('view_count', 0)
                    duration_str = f"{duration//60}m {duration%60}s" if duration else "Live Stream"
                    
                    st.markdown(f"### {title}")
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.markdown(f"**Channel:** {uploader}")
                    with col2:
                        st.markdown(f"**Duration:** {duration_str}")
                    
                    st.markdown(f"**Views:** {views:,}")

                # Thumbnail
                if thumbnail:
                    st.image(thumbnail, use_column_width=True)
                else:
                    st.info("Thumbnail not available for this content.")

                # Metadata Grid
                st.markdown('<div class="info-grid">', unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown('<div class="info-item">', unsafe_allow_html=True)
                    st.markdown('<div class="info-label">Format</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="info-value">{download_type}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown('<div class="info-item">', unsafe_allow_html=True)
                    st.markdown('<div class="info-label">Quality</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="info-value">{quality}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                with col3:
                    st.markdown('<div class="info-item">', unsafe_allow_html=True)
                    st.markdown('<div class="info-label">Type</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="info-value">{content_type}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                with col4:
                    st.markdown('<div class="info-item">', unsafe_allow_html=True)
                    st.markdown('<div class="info-label">Archive</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="info-value">ZIP</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)

                # Description
                description = info.get('description')
                if not description and is_playlist and info.get('entries'):
                    description = info['entries'][0].get('description', '') if info['entries'] else ''
                if description:
                    with st.expander("View Full Description"):
                        st.markdown(description)

                st.markdown('</div>', unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Failed to process URL: {str(e)}")
            info = None

# -------------------------- Download Action --------------------------
if url.strip() and info:
    if st.button("INITIATE DOWNLOAD", type="primary", use_container_width=True, key="download"):
        if not zip_filename.lower().endswith(".zip"):
            zip_filename += ".zip"

        with st.status("Processing download request...", expanded=True) as status:
            st.write("Establishing connection to YouTube servers...")
            try:
                zip_buffer = download_video_or_playlist(
                    url=url,
                    download_type=download_type.lower(),
                    quality=quality,
                    content_type=content_type,
                    zip_output=True
                )

                status.update(label="Download completed successfully", state="complete")
                st.success("Your files are ready for download.")
                
                st.download_button(
                    label="DOWNLOAD ARCHIVE",
                    data=zip_buffer,
                    file_name=zip_filename,
                    mime="application/zip",
                    use_container_width=True
                )

            except Exception as e:
                status.update(label="Download failed", state="error")
                st.error(f"Error during download: {e}")

# -------------------------- Footer --------------------------
st.markdown(f"""
<div class="footer">
    <strong>Ravana YT Downloader</strong> • Professional Edition v2.0<br>
    Developed by <strong>D. Abhiram</strong> • Secure • Fast • No Ads
</div>
""", unsafe_allow_html=True)
