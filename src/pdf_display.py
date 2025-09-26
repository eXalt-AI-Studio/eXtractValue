
import fitz  # PyMuPDF
from PIL import Image, ImageDraw
import streamlit as st

# Example bounding box from Textract (normalized coordinates)
bbox = {
    'Width': 0.6210066080093384,
    'Height': 0.022931816056370735,
    'Left': 0.09700631350278854,
    'Top': 0.12282328307628632
}

pdf_path = "data/fayet_bail_commercial.pdf"
doc = fitz.open(pdf_path)
num_pages = doc.page_count

st.title("PDF Viewer with Optional Bounding Box")

# Page selector
page_number = st.number_input(
    "Page number", min_value=1, max_value=num_pages, value=1, step=1
) - 1  # PyMuPDF uses 0-based index

# Toggle for bounding box
show_bbox = st.checkbox("Show bounding box", value=True)

page = doc.load_page(page_number)
pix = page.get_pixmap()
img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

if show_bbox:
    # Convert normalized bbox to pixel coordinates
    x0 = int(bbox['Left'] * pix.width)
    y0 = int(bbox['Top'] * pix.height)
    x1 = int((bbox['Left'] + bbox['Width']) * pix.width)
    y1 = int((bbox['Top'] + bbox['Height']) * pix.height)
    draw = ImageDraw.Draw(img)
    draw.rectangle([x0, y0, x1, y1], outline="red", width=3)
    st.image(img, caption=f"PDF page {page_number+1} with bounding box")
else:
    st.image(img, caption=f"PDF page {page_number+1}")