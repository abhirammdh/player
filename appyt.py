import streamlit as st
import time
import zipfile
import os
import tempfile
from io import BytesIO
from downloader import download_video_or_playlist

st.set_page_config(page_title="Paradox-Player", layout="centered")
st.title("Paradox-playerYT Downloader")

# Form layout for input
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
            # Create a temporary directory for downloads
            temp_dir = tempfile.mkdtemp()
            st.write(f"Using temp directory: {temp_dir}")  # Debug: Show temp dir

            for percent in range(0, 100, 10):
                time.sleep(0.2)  # Simulate work being done
                progress_bar.progress(percent + 10)
                elapsed = time.time() - start_time
                remaining = int((100 - percent) / 10 * 0.2)
                status_text.text(f"Downloading... {percent + 10}% | Estimated time left: {remaining}s")
            
            # Pass temp_dir to the function if it supports it; otherwise, assume it downloads to cwd
            # Adjust your downloader function to accept output_dir=temp_dir if possible
            result = download_video_or_playlist(
                url=url,
                download_type=download_type,
                quality=quality,
                content_type=content_type,
                zip_output=False,  # Get list of file paths
                output_dir=temp_dir  # Add this if your function supports it; otherwise, remove
            )
            
            st.write(f"Downloader returned: {result}")  # Debug: Show what was returned
            
            # Handle different return types
            if isinstance(result, list) and len(result) > 0:
                zip_buffer = BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    added_files = []
                    for file_path in result:
                        full_path = os.path.join(temp_dir, file_path) if not os.path.isabs(file_path) else file_path
                        if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
                            arcname = os.path.basename(full_path)
                            zipf.write(full_path, arcname)
                            added_files.append(arcname)
                            st.write(f"Added to ZIP: {arcname} (size: {os.path.getsize(full_path)} bytes)")  # Debug
                        else:
                            st.warning(f"File not found or empty: {full_path}")
                
                if added_files:
                    zip_buffer.seek(0)
                    if not zip_filename.endswith(".zip"):
                        zip_filename += ".zip"
                    st.success(f"Download complete. ZIP contains {len(added_files)} files: {', '.join(added_files)}")
                    st.download_button(
                        label="Download ZIP file",
                        data=zip_buffer,
                        file_name=zip_filename,
                        mime="application/zip"
                    )
                else:
                    st.error("No valid files were downloaded. Check the downloader function.")
            else:
                st.error(f"Unexpected result from downloader: {type(result)}. Expected list of file paths.")
                
        except Exception as e:
            st.error(f"Download failed: {e}")
            import traceback
            st.code(traceback.format_exc())  # Debug: Show full traceback

# Footer
st.markdown("""---""")
st.markdown("<div style='text-align: center; color: gray;'>Created by Sree</div>", unsafe_allow_html=True)
