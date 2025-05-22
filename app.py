# === MODULES ===
import streamlit as st
import pandas as pd
import numpy as np
import os
import re
import base64
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from io import BytesIO
from PIL import Image
from unidecode import unidecode
from datetime import datetime

# === CONFIG STREAMLIT ===
st.set_page_config(
    page_title="Prétraitement SEMrush",
    layout="wide",
    page_icon="https://raw.githubusercontent.com/Matkermo/Keywords/main/favicon.png"
)

# === BANNIÈRE ===
st.image("https://raw.githubusercontent.com/Matkermo/Keywords/main/Keyword_research_logo.png", use_container_width=True),

# === CSS PERSONNALISÉ ===
st.markdown("""
    <style>
    .block-container { padding-top: 0rem; }
    #MainMenu, footer { visibility: hidden; }

    .stApp {
        background-color: #1A472A;
        color: white;
    }
        /* Sidebar */
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] select,
    section[data-testid="stSidebar"] textarea,
    section[data-testid="stSidebar"] option {
        color: #222 !important;
        background: #fff !important;
    }
    /* Cacher l'en-tête de Streamlit */
    [data-testid="stHeader"] {
        background-color: rgba(0, 0, 0, 0); /* Couleur transparente */
        height: 0px; /* Supprime l'espace occupé */
        visibility: hidden; /* Masque l'élément */
    }

    /* Ajustement pour le contenu */
    .stApp > header {
        display: none; /* Cache complètement l'entête */
    }

    h1, h2, h3, h4 {
        color: #B9FBC0;
    }

    .css-1cpxqw2, .stDataFrame {
        background-color: white !important;
        color: black !important;
    }

    input, select, textarea, .stSlider, .stSelectbox, .stTextInput {
        color: black !important;
    }

    label, .stMarkdown {
        color: white !important;
    }

    .stButton>button {
        background-color: #B9FBC0;
        color: black;
        font-weight: bold;
    }

    [data-testid="stSidebar"] {
        background-color: #1A472A;
    }

    [data-testid="stSidebar"] * {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)
# === SIDEBAR OPTIONS ===
st.sidebar.title("Options de traitement")

uploaded_file = st.sidebar.file_uploader("Charger le fichier SEMrush (CSV)", type=["csv"])
branded_file = st.sidebar.file_uploader("Mots-clés de marque (CSV, une colonne)", type=["csv"])
stopwords_file = st.sidebar.file_uploader("Liste de stopwords personnalisés (optionnel)", type=["csv"])
terms_to_exclude = ['free', 'torrent', 'crack', 'pirate', 'illegal', 'mp3', 'streaming', 'download', 'youtube']

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("Fichier SEMrush chargé avec succès.")
    
    # Nettoyage de base
    df.dropna(subset=['Keyword'], inplace=True)
    df.drop_duplicates(subset=['Keyword'], inplace=True)
    
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')
    df['KD'] = pd.to_numeric(df['KD'], errors='coerce')
    df.dropna(subset=['Volume', 'KD'], inplace=True)

    df['Keyword'] = df['Keyword'].astype(str).str.lower().str.strip()
    df['word_count'] = df['Keyword'].apply(lambda x: len(x.split()))
    # Branded keywords
    if branded_file is not None:
        branded_keywords_df = pd.read_csv(branded_file)
        branded_list = branded_keywords_df.iloc[:, 0].dropna().astype(str).str.lower().tolist()
        df['Branded'] = df['Keyword'].apply(lambda kw: any(brand in kw for brand in branded_list))
    else:
        df['Branded'] = False

    # Application des filtres
    df_filtered = df[
        (df['Volume'] >= 100) &
        (df['KD'] <= 60) &
        (df['word_count'] >= 2) &
        (~df['Keyword'].str.contains('|'.join(terms_to_exclude), case=False, na=False)) &
        (df['Branded'] == False)
    ]

    st.subheader("Mots-clés filtrés")
    st.write(f"{len(df_filtered)} mots-clés restants après filtrage")
    st.dataframe(df_filtered)
    # === EXPORT CSV ===
    st.download_button(
        label="Télécharger le fichier filtré",
        data=df_filtered.to_csv(index=False).encode('utf-8'),
        file_name='keywords_filtrés.csv',
        mime='text/csv'
    )

    # === WORDCLOUD ===
    st.subheader("Nuage de mots (WordCloud)")
    if not df_filtered.empty:
        text = " ".join(df_filtered['Keyword'])
        if stopwords_file is not None:
            stopwords_df = pd.read_csv(stopwords_file)
            stopwords_list = stopwords_df.iloc[:, 0].dropna().astype(str).tolist()
            stopwords = set(stopwords_list)
        else:
            stopwords = set()

        wordcloud = WordCloud(
            width=1200,
            height=600,
            background_color='white',
            stopwords=stopwords,
            colormap='Greens'
        ).generate(text)

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)
    # === HISTOGRAMME VOLUME ===
    st.subheader("Répartition des volumes de recherche")
    fig_vol = px.histogram(df_filtered, x='Volume', nbins=50, title='Distribution du Volume')
    st.plotly_chart(fig_vol, use_container_width=True)

    # === HISTOGRAMME KD ===
    st.subheader("Répartition du Keyword Difficulty (KD)")
    fig_kd = px.histogram(df_filtered, x='KD', nbins=50, title='Distribution du KD')
    st.plotly_chart(fig_kd, use_container_width=True)

    # === HISTOGRAMME NB DE MOTS ===
    st.subheader("Répartition du nombre de mots par keyword")
    fig_wc = px.histogram(df_filtered, x='word_count', nbins=15, title='Nombre de mots dans les keywords')
    st.plotly_chart(fig_wc, use_container_width=True)

    # === HEATMAP DES CORRÉLATIONS ===
    st.subheader("Corrélations entre colonnes numériques")
    numeric_cols = df_filtered.select_dtypes(include=[np.number])
    if not numeric_cols.empty:
        corr = numeric_cols.corr()
        fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale='Greens', title='Heatmap de corrélation')
        st.plotly_chart(fig_corr, use_container_width=True)
    # === TÉLÉCHARGEMENT DE L’IMAGE DU WORDCLOUD ===
    st.subheader("Exporter le WordCloud en image")
    buffer = BytesIO()
    wordcloud.to_image().save(buffer, format="PNG")
    byte_im = buffer.getvalue()

    st.download_button(
        label="Télécharger le WordCloud",
        data=byte_im,
        file_name="wordcloud_keywords.png",
        mime="image/png"
    )

else:
    st.warning("Veuillez charger un fichier SEMrush et une liste de branded keywords pour démarrer le traitement.")
