import streamlit as st
import rawpy
import numpy as np
from PIL import Image
import io

st.title("Batch ARW to PNG Converter")

st.write(
    """
    Upload one or more Sony ARW (RAW) images. The app will convert all to PNG format, optimizing for smaller file size while maintaining high quality.
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
    for uploaded_file in uploaded_files:
        st.write(f"**Processing:** {uploaded_file.name}")
        try:
            arw_bytes = uploaded_file.read()
            png_buf = arw_to_png(arw_bytes)
            st.image(png_buf, caption=f"Converted: {uploaded_file.name}", use_column_width=True)
            st.download_button(
                label=f"Download {uploaded_file.name.replace('.arw', '.png')}",
                data=png_buf,
                file_name=uploaded_file.name.replace(".arw", ".png"),
                mime="image/png"
            )
            st.success(f"Conversion successful for {uploaded_file.name}!")
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {e}")
