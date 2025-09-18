import os
import streamlit as st
import pandas as pd
import fitz
from annual_rent import get_annual_rents
from llm_chat import call_llm_chat
from dotenv import load_dotenv
import plotly.graph_objects as go

load_dotenv()
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("Missing OPENROUTER_API_KEY")

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

st.markdown(
    """
    <style>
    .stDownloadButton button {
        background-color: #5853FF !important;
        color: white !important;
    }
    div.stButton > button:first-child {
        background-color: #5853FF !important;
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

header_col1, header_col2, header_col3 = st.columns([1, 1, 8])
with header_col1:
    st.image("src/images/logo-exalt-2.png", width=100)
with header_col2:
    st.image("src/images/logo-AEW.png", width=100)
with header_col3:
    st.markdown("<h3 style='color: #5853FF; margin: 0;'>Données Baux Commerciaux</h3>", unsafe_allow_html=True)

select_col, _ = st.columns([1, 4])
with select_col:
    selected_file = st.selectbox("Sélectionner un bail commercial:", list_files)
filtered_df = df[df['filename'] == selected_file]
    
tab_names = ["Extraction", "Question", "Analyse Automatique", "Chronologie"]
tab1, tab2, tab3, tab4 = st.tabs(tab_names)

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
        if not filtered_df.empty:
            record = filtered_df.iloc[0].to_dict()
            for key, value in record.items():
                if key == 'filename':
                    continue
                st.text_input(label=key, value=str(value), key=f"{selected_file}_{key}")
            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Télécharger les données extraites en CSV",
                data=csv,
                file_name=f"{selected_file.replace('.pdf', '_extracted_data.csv')}",
                mime='text/csv',
            )
        else:
            st.info("Aucune donnée extraite pour ce fichier.")

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Texte Extrait :")
        if not filtered_df.empty:
            txt_path = f"output/{selected_file.replace('.pdf', '.txt')}"
            if os.path.exists(txt_path):
                with open(txt_path, "r", encoding="utf-8") as txt_file:
                    text_content = txt_file.read()
                st.text_area("Contenu texte extrait du PDF :", text_content, height=1000)
        else:
            st.info("Aucun fichier texte extrait trouvé pour ce PDF.")
    with col2:
        st.subheader("Saisir une question :")
        user_question = st.text_area("Votre question :", value="Quelles sont les clauses qui peuvent poser problème juridiquement ?", height=80)
        if st.button("Envoyer la question"):
            response, usage = call_llm_chat(
                "You are a helpful assistant.",
                user_question,
                text_content,
                temperature=0.0
            )
            st.write(response)

with tab3:
    col1, col2 = st.columns(2)
    if not filtered_df.empty:
        annual_rents = get_annual_rents(filtered_df)
    with col1:
        st.subheader("Echéancier des loyers minimaux :")
        if not annual_rents.empty:
            st.dataframe(annual_rents)
    with col2:
        st.subheader("Visualisation des loyers minimaux :")
        if not annual_rents.empty:
            chart_data = annual_rents.copy()
            year_col = 'Year' if 'Year' in chart_data.columns else 'Année'
            rent_col = 'Expected Rent (€)' if 'Expected Rent (€)' in chart_data.columns else 'Loyer attendu (€)'
            if year_col in chart_data.columns and rent_col in chart_data.columns:
                st.bar_chart(data=chart_data, x=year_col, y=rent_col, use_container_width=True)

with tab4:
    st.subheader("Chronologie :")
    if not filtered_df.empty:
        start_date = pd.to_datetime(filtered_df.iloc[0].get("Date de début"))
        end_date = pd.to_datetime(filtered_df.iloc[0].get("Date d'expiration"))
        signature_date = pd.to_datetime(filtered_df.iloc[0].get("Date de signature du bail"))
        timeline_df = pd.DataFrame({
            "Event": ["Début", "Expiration", "Signature"],
            "Date": [start_date, end_date, signature_date]
        })
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=timeline_df["Date"],
            y=[1, 1, 1],
            mode="markers+text+lines",
            marker=dict(size=16, color="#5853FF"),
            text=timeline_df["Event"],
            textposition="top center",
            line=dict(color="#5853FF", width=4),
            hoverinfo="text+x"
        ))
        fig.update_layout(
            showlegend=False,
            yaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
            xaxis_title="Date",
            margin=dict(l=20, r=20, t=30, b=20),
            height=180
        )
        st.plotly_chart(fig, use_container_width=True)

