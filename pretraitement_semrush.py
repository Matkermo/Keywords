import streamlit as st
import pandas as pd
from io import BytesIO
import plotly.express as px
import re

# 💬 Paramètres langues et textes
country_flags = {
    "FR": ":flag-fr:",  # Emoji du drapeau français
    "EN": ":us:"        # Emoji du drapeau américain
}
LANG_OPTIONS = [f"FR {country_flags['FR']}", f"EN {country_flags['EN']}"]
LANG_CODES = {f"FR {country_flags['FR']}": "FR", f"EN {country_flags['EN']}": "EN"}

TEXTS = {
    "FR": {
        "app_title": "Pré-traitement SEO : Branded & Non-branded",
        "app_desc": "Chargez plusieurs fichiers SEMrush et vos mots spécifiques pour séparer les mots-clés branded et non-branded.",
        "upload_label": "Fichiers SEMrush (.csv, .xlsx)",
        "min_volume": "Volume minimum",
        "max_kd": "Difficulté KD max (%)",
        "brands_list": "Mots-clés branded",
        "manual_brands": "Entrez vos mots spécifiques (1 par ligne)",
        "brand_file": "Ou importez un fichier de mots branded (txt, csv ou xlsx)",
        "run": "Lancer le pré-traitement",
        "synth_title": "Synthèse par source",
        "kw_total": "KW total",
        "kw_brand": "KW branded",
        "kw_nonbrand": "KW non-branded",
        "hard_kd": "Hard KD",
        "low_volume": "Low Volume",
        "pct_brand": "% branded",
        "pct_nonbrand": "% non-branded",
        "dl_label": "Télécharger résultats CSV",
        "dl_filename": "kw_filtrés.csv",
        "n_lines": "Traitement terminé ({:d} lignes)",
        "info_upload": "Veuillez charger au moins un fichier SEMrush.",
        "error_keyword": "Colonne 'Keyword' introuvable ! Colonnes dispo:",
        "error_parse": "Erreur de chargement :",
        "no_data": "Aucune donnée exploitable. Vérifiez vos fichiers.",
        "total": "TOTAL",
        "true": "VRAI",
        "false": "FAUX"
    },
    "EN": {
        "app_title": "SEO Pre-processing: Branded & Non-branded",
        "app_desc": "Upload one or more SEMrush files and your brands to separate branded and non-branded keywords.",
        "upload_label": "SEMrush files (.csv, .xlsx)",
        "min_volume": "Minimum search volume",
        "max_kd": "Max KD (%)",
        "brands_list": "Brand keywords",
        "manual_brands": "Enter specifics words/brands (one per line)",
        "brand_file": "Or import a list of branded keywords (txt, csv, xlsx)",
        "run": "Run pre-processing",
        "synth_title": "Summary per source",
        "kw_total": "KW total",
        "kw_brand": "KW branded",
        "kw_nonbrand": "KW non-branded",
        "hard_kd": "Hard KD",
        "low_volume": "Low Volume",
        "pct_brand": "% branded",
        "pct_nonbrand": "% non-branded",
        "dl_label": "Download CSV results",
        "dl_filename": "filtered_kw.csv",
        "n_lines": "Done ({:d} rows processed)",
        "info_upload": "Please upload at least one SEMrush file.",
        "error_keyword": "'Keyword' column not found! Available columns:",
        "error_parse": "Loading error:",
        "no_data": "No usable data. Check your files.",
        "total": "TOTAL",
        "true": "TRUE",
        "false": "FALSE"
    }
}

# 💬 Fonctions métiers
def is_branded_kw(keyword, brand_set):
    lower_keyword = str(keyword).lower()
    keyword_words = re.findall(r"\b[\w'-]+\b", lower_keyword)
    for brand in brand_set:
        brand = str(brand).strip().lower()
        if not brand:
            continue
        if len(brand) <= 3:
            if brand in keyword_words:
                return True
        else:
            if brand in lower_keyword:
                return True
    return False

# 💬 Config Streamlit
st.set_page_config(layout="wide")

# 💬 Barres latérales et langue
col1, colspace, col2 = st.columns([6, 2, 1])
with col2:
    select_lang = st.selectbox("", LANG_OPTIONS, label_visibility='collapsed')
langue = LANG_CODES[select_lang]

# 💬 Titre et description
st.title(TEXTS[langue]["app_title"])
st.markdown(TEXTS[langue]["app_desc"])

# 🟢 Sidebar Pro IU
with st.sidebar:
    st.header("Imports SEMrush")
    uploaded_files = st.file_uploader(TEXTS[langue]["upload_label"], accept_multiple_files=True)
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        min_volume = st.number_input(TEXTS[langue]["min_volume"], min_value=0, value=0)
    
    with col2:
        max_kd = st.number_input(TEXTS[langue]["max_kd"], min_value=0, max_value=100, value=100)

    st.markdown("---")
    st.write(TEXTS[langue]["brands_list"])
    brand_input = st.text_area(TEXTS[langue]["manual_brands"], height=100)
    brand_file = st.file_uploader(TEXTS[langue]["brand_file"], type=["txt", "csv", "xlsx"])
    run_btn = st.button(TEXTS[langue]["run"])

# 🟡 Définition des couleurs par défaut pour chaque onglet
default_colors = {
    "synthese": ["#4CAF50", "#FF9800", "#2196F3", "#F44336"],
}

# Génération dynamique des couleurs pour chaque onglet
for idx in range(1, 16):
    default_colors[f"onglet{idx}"] = [px.colors.qualitative.Plotly[idx % len(px.colors.qualitative.Plotly)]]

if uploaded_files and run_btn:
    # 💬 Création du set branded à partir du textarea et des fichiers
    brand_set = set([b.strip() for b in brand_input.splitlines() if b.strip()]) if brand_input else set()
    if brand_file:
        if brand_file.type == "text/plain":
            txt_lines = brand_file.read().decode('utf-8').splitlines()
            brand_set.update([b.strip() for b in txt_lines if b.strip()])
        elif brand_file.type in [
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel"]:
            df_brands = pd.read_excel(brand_file, header=None)
            brand_set.update(df_brands[0].dropna().astype(str).str.strip())
        elif brand_file.type == "text/csv":
            df_brands = pd.read_csv(brand_file, header=None)
            brand_set.update(df_brands[0].dropna().astype(str).str.strip())

    progress = st.progress(0)
    synthese = []
    all_processed = []

    for i, upl in enumerate(uploaded_files):
        try:
            if upl.type == "text/csv":
                df = pd.read_csv(upl)
            else:
                df = pd.read_excel(upl)
            if 'Keyword' not in df.columns:
                st.error(f"{TEXTS[langue]['error_keyword']} {list(df.columns)}")
                continue
            df['Search Volume'] = pd.to_numeric(df['Search Volume'], errors='coerce').fillna(0)
            df['Keyword Difficulty'] = pd.to_numeric(df['Keyword Difficulty'], errors='coerce').fillna(0)

            # Ajoute nom du fichier pour le détail
            df['Fichier'] = upl.name

            # 💬 Ajout colonne tagged branded
            branded_col = [
                TEXTS[langue]["true"] if is_branded_kw(kw, brand_set) else TEXTS[langue]["false"]
                for kw in df['Keyword']
            ]
            idx_kw = df.columns.get_loc('Keyword')
            df.insert(idx_kw + 1, 'branded', branded_col)

            # 💬 Ajout colonne catégorie LV/HardKD
            category_col = []
            for _, row in df.iterrows():
                if row['Search Volume'] < min_volume:
                    category_col.append("Low Volume")
                elif row['Keyword Difficulty'] > max_kd:
                    category_col.append("Hard KD")
                else:
                    category_col.append("")
            df.insert(idx_kw + 2, 'Category', category_col)

            mask_category_empty = (df['Category'] == "")
            mask_branded = df['branded'] == TEXTS[langue]["true"]
            mask_nonbranded = df['branded'] == TEXTS[langue]["false"]

            n_total = len(df)
            n_kwbrand = ((mask_category_empty) & (mask_branded)).sum()
            n_kwnonbrand = ((mask_category_empty) & (mask_nonbranded)).sum()
            n_hardkd = (df['Category'] == "Hard KD").sum()
            n_lowvol = (df['Category'] == "Low Volume").sum()

            brand_pct = f"{100 * n_kwbrand / n_total:.1f}%" if n_total > 0 else "0%"
            nonbrand_pct = f"{100 * n_kwnonbrand / n_total:.1f}%" if n_total > 0 else "0%"

            synthese.append({
                "Fichier": upl.name,
                TEXTS[langue]["kw_total"]: n_total,
                TEXTS[langue]["kw_brand"]: n_kwbrand,
                TEXTS[langue]["kw_nonbrand"]: n_kwnonbrand,
                TEXTS[langue]["hard_kd"]: n_hardkd,
                TEXTS[langue]["low_volume"]: n_lowvol,
                TEXTS[langue]["pct_brand"]: brand_pct,
                TEXTS[langue]["pct_nonbrand"]: nonbrand_pct,
            })

            all_processed.append(df)

            st.write(f"✅ {upl.name}: {n_total} lignes chargées")
        except Exception as e:
            st.error(f"{TEXTS[langue]['error_parse']} {e}")
        progress.progress(int(100 * (i + 1) / len(uploaded_files)))

    if all_processed:
        fusion = pd.concat(all_processed, ignore_index=True)
        synthese_df = pd.DataFrame(synthese)

        # 💬 Ajout ligne total
        if not synthese_df.empty:
            total_kw = synthese_df[TEXTS[langue]["kw_total"]].sum()
            total_branded = synthese_df[TEXTS[langue]["kw_brand"]].sum()
            total_nonbranded = synthese_df[TEXTS[langue]["kw_nonbrand"]].sum()
            total_hardkd = synthese_df[TEXTS[langue]["hard_kd"]].sum()
            total_lowvol = synthese_df[TEXTS[langue]["low_volume"]].sum()
            total_row = {
                "Fichier": TEXTS[langue]["total"],
                TEXTS[langue]["kw_total"]: total_kw,
                TEXTS[langue]["kw_brand"]: total_branded,
                TEXTS[langue]["kw_nonbrand"]: total_nonbranded,
                TEXTS[langue]["hard_kd"]: total_hardkd,
                TEXTS[langue]["low_volume"]: total_lowvol,
                TEXTS[langue]["pct_brand"]: f"{100 * total_branded / total_kw:.1f}%" if total_kw > 0 else "0%",
                TEXTS[langue]["pct_nonbrand"]: f"{100 * total_nonbranded / total_kw:.1f}%" if total_kw > 0 else "0%",
            }
            synthese_df = pd.concat([synthese_df, pd.DataFrame([total_row])], ignore_index=True)

        st.success(TEXTS[langue]["n_lines"].format(len(fusion)))

        # 🟢 ----- AFFICHAGE par Onglets --------
        tabs = st.tabs(["📊 Synthèse"] + [fname.split('.')[0] for fname in fusion['Fichier'].unique()] + ["🔍 Données brutes"])

        # Onglet Synthèse Globale
        with tabs[0]:
            st.subheader("🔎 " + TEXTS[langue]["synth_title"])
            st.dataframe(
                synthese_df,
                use_container_width=True,
                height=min(600, 60 + 30 * len(synthese_df))
            )

            # Bouton de téléchargement pour la synthèse
            @st.fragment
            def download_synth_data():
                st.download_button(
                    label=TEXTS[langue]["dl_label"],
                    icon="📥",
                    data=synthese_df.to_csv(index=False),
                    file_name="synthese.csv",
                    mime="text/csv",
                    use_container_width=True,
                    disabled=synthese_df.empty
                )

            download_synth_data()

            # Pie chart et bar chart
            synth_global_row = synthese_df[synthese_df["Fichier"] == TEXTS[langue]["total"]]
            if not synth_global_row.empty:
                colpie, colbar = st.columns(2)
                # -- Pie
                with colpie:
                    values = [
                        int(synth_global_row[TEXTS[langue]["kw_nonbrand"]].values[0]),
                        int(synth_global_row[TEXTS[langue]["kw_brand"]].values[0]),
                        int(synth_global_row[TEXTS[langue]["hard_kd"]].values[0]),
                        int(synth_global_row[TEXTS[langue]["low_volume"]].values[0])
                    ]
                    labels = [
                        TEXTS[langue]["kw_nonbrand"],
                        TEXTS[langue]["kw_brand"],
                        TEXTS[langue]["hard_kd"],
                        TEXTS[langue]["low_volume"]
                    ]
                    colors = default_colors["synthese"]
                    fig1 = px.pie(
                        names=labels,
                        values=values,
                        color=labels,
                        color_discrete_sequence=colors,
                        title="Répartition globale des mots-clés"
                    )
                    fig1.update_traces(textinfo='percent+label')
                    st.plotly_chart(fig1, use_container_width=True)
                # -- Bar
                with colbar:
                    fig2 = px.bar(
                        x=labels,
                        y=values,
                        color=labels,
                        color_discrete_sequence=colors,
                        title="Distribution globale"
                    )
                    st.plotly_chart(fig2, use_container_width=True)

        # --- Onglet par fichier avec graphiques ---
        for idx in range(1, len(tabs) - 1):
            fname = fusion['Fichier'].unique()[idx - 1]
            with tabs[idx]:
                st.subheader(f"Analyse pour {fname}")
                file_data = fusion[fusion["Fichier"] == fname]
                n_total = len(file_data)
                n_kwbrand = (file_data['branded'] == TEXTS[langue]["true"]).sum()
                n_kwnonbrand = (file_data['branded'] == TEXTS[langue]["false"]).sum()
                n_hardkd = (file_data['Category'] == "Hard KD").sum()
                n_lowvol = (file_data['Category'] == "Low Volume").sum()

                brand_pct = f"{100 * n_kwbrand / n_total:.1f}%" if n_total > 0 else "0%"
                nonbrand_pct = f"{100 * n_kwnonbrand / n_total:.1f}%" if n_total > 0 else "0%"

                colors = default_colors[f"onglet{idx}"]

                fig3 = px.pie(
                    names=[TEXTS[langue]["kw_brand"], TEXTS[langue]["kw_nonbrand"]],
                    values=[n_kwbrand, n_kwnonbrand],
                    color_discrete_sequence=colors,
                    title=f"Distribution des mots-clés pour {fname}"
                )
                st.plotly_chart(fig3, use_container_width=True)

                fig4 = px.bar(
                    x=["Hard KD", "Low Volume"],
                    y=[n_hardkd, n_lowvol],
                    color_discrete_sequence=colors,
                    title=f"Répartition des catégories pour {fname}"
                )
                st.plotly_chart(fig4, use_container_width=True)

                # Affichage des 20 premières lignes
                st.write("### Aperçu des 20 premières lignes")
                st.dataframe(file_data.head(20), use_container_width=True)

                # Bouton de téléchargement pour chaque fichier
                @st.fragment
                def download_file_data():
                    st.download_button(
                        label=TEXTS[langue]["dl_label"],
                        icon="📥",
                        data=file_data.to_csv(index=False),
                        file_name=f"{fname.split('.')[0]}_data.csv",
                        mime="text/csv",
                        use_container_width=True,
                        disabled=file_data.empty
                    )

                download_file_data()

        # --- Onglet données brutes ---
        with tabs[-1]:
            st.subheader("🔍 Données brutes")
            st.write("Aperçu des données traitées :")
            st.dataframe(fusion, use_container_width=True)

            # 🔄 Fonction de téléchargement avec st.fragment
            @st.fragment
            def download_data():
                st.download_button(
                    label=TEXTS[langue]["dl_label"],
                    icon="📥",
                    data=fusion.to_csv(index=False),
                    file_name=TEXTS[langue]["dl_filename"],
                    mime="text/csv",
                    use_container_width=True,
                    disabled=fusion.empty
                )

            download_data()

    else:
        st.warning(TEXTS[langue]["no_data"])
else:
    st.info(TEXTS[langue]["info_upload"])
