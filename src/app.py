import streamlit as st
import pandas as pd
from datetime import datetime

# Load data from CSV
df = pd.read_csv('output/output_text.csv')


header_col1, header_col2 = st.columns([1, 8])
with header_col1:
    st.image("src/images/logo-exalt-2.png", width=170)
with header_col2:
    st.markdown("<h1 style='color: #5853FF; margin: 0;'>Extraction des données des Baux Commerciaux</h1>", unsafe_allow_html=True)

