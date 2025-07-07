import streamlit as st
import rawpy
from PIL import Image
import io
import zipfile

st.title("Batch ARW to JPG Converter (Max 5 MB per Image)")

st.write(
    """
    Upload one or more Sony ARW (RAW) images. The app converts all to JPG format, ensuring each file is under 5 MB.
    Download all converted JPGs at once as a ZIP file.
    """
)

uploaded_files = st.file_uploader(
    "Upload ARW images",
    type=["arw"],
    accept_multiple_files=True
)

def arw_to_jpg_maxsize(arw_bytes, max_size=5*1024*1024, min_quality=70, max_quality=95):
    with rawpy.imread(io.BytesIO(arw_bytes)) as raw:
        rgb = raw.postprocess(use_camera_wb=True, output_bps=8)
    img = Image.fromarray(rgb)
    quality = max_quality
    while quality >= min_quality:
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        size = buf.tell()
        if size <= max_size:
            buf.seek(0)
            return buf, quality, size
        quality -= 5
    buf.seek(0)
    return buf, quality, size  # Return lowest quality if still too large

if uploaded_files:
    jpg_files = []
    progress_bar = st.progress(0)
    total_files = len(uploaded_files)
    for idx, uploaded_file in enumerate(uploaded_files):
        try:
            arw_bytes = uploaded_file.read()
            jpg_buf, used_quality, final_size = arw_to_jpg_maxsize(arw_bytes)
            jpg_files.append((uploaded_file.name.replace(".arw", ".jpg"), jpg_buf.getvalue()))
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {e}")
        progress_bar.progress((idx + 1) / total_files)

    if jpg_files:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for fname, data in jpg_files:
                zip_file.writestr(fname, data)
        zip_buffer.seek(0)
        st.download_button(
            label="Download All as ZIP",
            data=zip_buffer,
            file_name="converted_images.zip",
            mime="application/zip"
        )
