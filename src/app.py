import os
import streamlit as st
import pandas as pd
import fitz

# Load data from CSV
df = pd.read_csv('output/output_text.csv')

list_files = ["fayet_bail_commercial.pdf",
            "Q448 ANTIBES - 0707 Bail_biff.pdf",
            "bail type SLB - Foncire Des Murs - 29 mai 2007_biff.pdf",
            "cong + bail VILLEPINTE FQ 1er tage_biff.pdf",
            "cong + bail VILLEPINTE FQ 2me tage_biff.pdf",
            "cong + bail VILLEPINTE QR 1er tage_biff.pdf",
            "Q145 CREIL - 0909 LGAI_biff.pdf",
            "Q153 FAYET - 1002 LGAI_biff.pdf",
            "Q241 BESANCON CHATEAUFARINE - 0709 ssbail commercial_biff.pdf",
            "Bail FQ - Saint Etienne_biff.pdf",
            "bail LA PLAINE_biff.pdf"]

st.set_page_config(
    page_title="Exalt & AEW",
    page_icon=":bar_chart:",
    layout="wide"
)

header_col1, header_col2 = st.columns([1, 8])
with header_col1:
    st.image("src/images/logo-exalt-2.png", width=100)
with header_col2:
    st.markdown("<h3 style='color: #5853FF; margin: 0;'>Données Baux Commerciaux</h3>", unsafe_allow_html=True)

selected_file = st.selectbox("Sélectionner un bail commercial:", list_files)
filtered_df = df[df['filename'] == selected_file]
    
tab_names = ["Extraction", "Analyse"]
tab1, tab2 = st.tabs(tab_names)

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Contenu du PDF:")
        if os.path.exists(f"data/{selected_file}"):   
            try:
                doc = fitz.open(f"data/{selected_file}")
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    pix = page.get_pixmap()
                    st.image(pix.tobytes(), caption=f"Page {page_num+1}", width='stretch')
            except Exception as e:
                st.error(f"Error displaying PDF: {e}")
    with col2:
        st.subheader("Données Clées Extraites:")
        # Display as key-value pairs (vertical)
        if not filtered_df.empty:
            record = filtered_df.iloc[0].to_dict()
            for key, value in record.items():
                if key == 'filename':
                    continue
                st.write(f"**{key}**: {value}")
        else:
            st.info("Aucune donnée extraite pour ce fichier.")
