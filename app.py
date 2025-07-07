import streamlit as st
import rawpy
import numpy as np
from PIL import Image
import io
import zipfile

st.title("Batch ARW to PNG Converter")

st.write(
    """
    Upload one or more Sony ARW (RAW) images. The app will convert all to PNG format, optimizing for smaller file size while maintaining high quality.
    Download all converted PNGs at once as a ZIP file.
    """
)

uploaded_files = st.file_uploader(
    "Upload ARW images",
    type=["arw"],
    accept_multiple_files=True
)

def arw_to_png(arw_bytes, quantize_colors=256):
    with rawpy.imread(io.BytesIO(arw_bytes)) as raw:
        rgb = raw.postprocess(
            use_camera_wb=True,
            output_bps=8
        )
    img = Image.fromarray(rgb)
    img = img.quantize(colors=quantize_colors, method=Image.FASTOCTREE)
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    buf.seek(0)
    return buf

if uploaded_files:
    png_files = []
    for uploaded_file in uploaded_files:
        st.write(f"**Processing:** {uploaded_file.name}")
        try:
            arw_bytes = uploaded_file.read()
            png_buf = arw_to_png(arw_bytes)
            png_files.append((uploaded_file.name.replace(".arw", ".png"), png_buf.getvalue()))
            st.image(png_buf, caption=f"Converted: {uploaded_file.name}", use_container_width=True)
            st.success(f"Conversion successful for {uploaded_file.name}!")
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {e}")

    if png_files:
        # Create ZIP in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for fname, data in png_files:
                zip_file.writestr(fname, data)
        zip_buffer.seek(0)

        st.download_button(
            label="Download All as ZIP",
            data=zip_buffer,
            file_name="converted_images.zip",
            mime="application/zip"
        )
