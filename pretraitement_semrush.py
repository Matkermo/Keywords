import streamlit as st
import pandas as pd
from io import BytesIO
import re

# Emoji drapeaux pour menu
country_flags = {
    "FR": "🇫🇷",
    "EN": "🇺🇸"
}

LANG_OPTIONS = [
    f"FR {country_flags['FR']}",
    f"EN {country_flags['EN']}"
]

LANG_CODES = {
    f"FR {country_flags['FR']}": "FR",
    f"EN {country_flags['EN']}": "EN"
}

# ----- Textes multilingues -----
TEXTS = {
    "FR": {
        "app_title": "Pré-traitement SEMrush SEO : Branded & Non-branded",
        "app_desc": "Chargez plusieurs fichiers SEMrush et vos marques pour séparer les requêtes de marque et hors marque.",
        "upload_label": "Fichiers SEMrush (.csv, .xlsx)",
        "min_volume": "Volume minimum",
        "max_kd": "Difficulté KD max (%)",
        "brands_list": "Mots-clés de marque (branded)",
        "manual_brands": "Entrez vos marques (1 par ligne)",
        "brand_file": "Ou importez un fichier de mots branded (txt, csv ou xlsx)",
        "run": "Lancer le pré-traitement",
        "synth_title": "Synthèse par source",
        "kw_total": "KW total",
        "kw_brand": "KW branded",
        "kw_nonbrand": "KW non-branded",
        "pct_brand": "% branded",
        "pct_nonbrand": "% non-branded",
        "dl_label": "Télécharger résultats Excel",
        "dl_filename": "kw_filtrés.xlsx",
        "n_lines": "Traitement terminé ({:d} lignes)",
        "info_upload": "Veuillez charger au moins un fichier SEMrush.",
        "error_keyword": "Colonne 'Keyword' introuvable ! Colonnes dispo:",
        "error_parse": "Erreur de chargement :",
        "no_data": "Aucune donnée exploitable. Vérifiez vos fichiers.",
        "total": "TOTAL",
        "true": "VRAI",
        "false": "FAUX",
        "branded": "Branded",
        "reason": "reason"
    },
    "EN": {
        "app_title": "SEMrush SEO Pre-processing: Branded & Non-branded",
        "app_desc": "Upload one or more SEMrush files and your brands to separate branded and non-branded queries.",
        "upload_label": "SEMrush files (.csv, .xlsx)",
        "min_volume": "Minimum search volume",
        "max_kd": "Max KD (%)",
        "brands_list": "Brand keywords",
        "manual_brands": "Enter brands (one per line)",
        "brand_file": "Or import a list of branded keywords (txt, csv, xlsx)",
        "run": "Run pre-processing",
        "synth_title": "Summary per source",
        "kw_total": "KW total",
        "kw_brand": "KW branded",
        "kw_nonbrand": "KW non-branded",
        "pct_brand": "% branded",
        "pct_nonbrand": "% non-branded",
        "dl_label": "Download Excel results",
        "dl_filename": "filtered_kw.xlsx",
        "n_lines": "Done ({:d} rows processed)",
        "info_upload": "Please upload at least one SEMrush file.",
        "error_keyword": "'Keyword' column not found! Available columns:",
        "error_parse": "Loading error:",
        "no_data": "No usable data. Check your files.",
        "total": "TOTAL",
        "true": "TRUE",
        "false": "FALSE",
        "branded": "Branded",
        "reason": "reason"
    }
}

def is_branded_kw(keyword, brand_set):
    lower_keyword = str(keyword).lower()
    keyword_words = re.findall(r"\b[\w'-]+\b", lower_keyword)
    for brand in brand_set:
        brand = brand.strip().lower()
        if not brand:
            continue
        if len(brand) <= 3:
            if brand in keyword_words:
                return (1, brand)
        else:
            if brand in lower_keyword:
                return (1, brand)
    return (0, "")

st.set_page_config(layout="wide")
# Barre de langue en haut à droite
col1, colspace, col2 = st.columns([6, 2, 1])
with col2:
    select_lang = st.selectbox("", LANG_OPTIONS, label_visibility='collapsed')
langue = LANG_CODES[select_lang]

st.title(TEXTS[langue]["app_title"])
st.markdown(TEXTS[langue]["app_desc"])

uploaded_files = st.file_uploader(TEXTS[langue]["upload_label"], accept_multiple_files=True)

if uploaded_files:
    min_volume = st.number_input(TEXTS[langue]["min_volume"], min_value=0, value=0, key="min_volume")
    max_kd = st.number_input(TEXTS[langue]["max_kd"], min_value=0, max_value=100, value=100, key="max_kd")

    brand_input = st.text_area(TEXTS[langue]["manual_brands"], height=150, key="manual_brands")
    brand_file = st.file_uploader(TEXTS[langue]["brand_file"], type=["txt", "csv", "xlsx"], key="brand_file")

    if st.button(TEXTS[langue]["run"], key="run_button"):
        brand_set = set([b.strip() for b in brand_input.splitlines() if b.strip()]) if brand_input else set()

        if brand_file:
            if brand_file.type == "text/plain":
                txt_lines = brand_file.read().decode('utf-8').splitlines()
                brand_set.update([b.strip() for b in txt_lines if b.strip()])
            elif brand_file.type in [
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/vnd.ms-excel"
            ]:
                df_brands = pd.read_excel(brand_file, header=None)
                brand_set.update(df_brands[0].dropna().astype(str).str.strip())
            elif brand_file.type in ["text/csv"]:
                df_brands = pd.read_csv(brand_file, header=None)
                brand_set.update(df_brands[0].dropna().astype(str).str.strip())

        progress = st.progress(0)
        synthese = []
        all_processed = []

        for i, upl in enumerate(uploaded_files):
            try:
                if upl.type == "text/csv":
                    df = pd.read_csv(upl, dtype=str)
                else:
                    df = pd.read_excel(upl, dtype=str)

                if 'Keyword' not in df.columns:
                    st.error(f"{TEXTS[langue]['error_keyword']} {list(df.columns)}")
                    continue

                # conversion Search Volume & Keyword Difficulty
                df['Search Volume'] = pd.to_numeric(df['Search Volume'], errors='coerce').fillna(0)
                df['Keyword Difficulty'] = pd.to_numeric(df['Keyword Difficulty'], errors='coerce').fillna(0)

                # ----- AJOUT DE LA COLONNE CATEGORY -----
                def get_category(row):
                    if row['Keyword Difficulty'] > max_kd:
                        return "hard KD"
                    elif row['Search Volume'] < min_volume:
                        return "low search volume"
                    else:
                        return ""
                df['Category'] = df.apply(get_category, axis=1)
                # Insert 'Category' juste après 'Keyword'
                kw_idx = df.columns.get_loc('Keyword')
                categories = df.pop('Category')
                df.insert(kw_idx + 1, 'Category', categories)

                # --- FILTRAGE CLASSIQUE BRANDED/NON-BRANDED ---
                filtered_df = df[(df['Search Volume'] >= min_volume) & (df['Keyword Difficulty'] <= max_kd)].copy()
                branded_results = filtered_df['Keyword'].map(lambda x: is_branded_kw(x, brand_set))
                filtered_df[TEXTS[langue]["branded"]] = branded_results.map(lambda x: TEXTS[langue]["true"] if x[0] else TEXTS[langue]["false"])
                filtered_df[TEXTS[langue]["reason"]] = branded_results.map(lambda x: x[1])

                nb_branded = sum(filtered_df[TEXTS[langue]["branded"]] == TEXTS[langue]["true"])
                nb_total = len(filtered_df)
                synthese.append({
                    "Fichier": upl.name,
                    TEXTS[langue]["kw_total"]: nb_total,
                    TEXTS[langue]["kw_brand"]: nb_branded,
                    TEXTS[langue]["kw_nonbrand"]: nb_total - nb_branded,
                    TEXTS[langue]["pct_brand"]: f"{100 * nb_branded / nb_total:.1f}%" if nb_total > 0 else "0%",
                    TEXTS[langue]["pct_nonbrand"]: f"{100 * (nb_total - nb_branded) / nb_total:.1f}%" if nb_total > 0 else "0%",
                })
                all_processed.append(filtered_df)

                st.write(f"✅ {upl.name}: {nb_total} lignes traitées")
            except Exception as e:
                st.error(f"{TEXTS[langue]['error_parse']} {e}")
            progress.progress(int(100 * (i + 1) / len(uploaded_files)))

        if all_processed:
            fusion = pd.concat(all_processed, ignore_index=True)
            synthese_df = pd.DataFrame(synthese)
            # Ajout ligne TOTAL
            if not synthese_df.empty:
                total_kw = synthese_df[TEXTS[langue]["kw_total"]].sum()
                total_branded = synthese_df[TEXTS[langue]["kw_brand"]].sum()
                total_nonbranded = synthese_df[TEXTS[langue]["kw_nonbrand"]].sum()
                total_row = {
                    "Fichier": TEXTS[langue]["total"],
                    TEXTS[langue]["kw_total"]: total_kw,
                    TEXTS[langue]["kw_brand"]: total_branded,
                    TEXTS[langue]["kw_nonbrand"]: total_nonbranded,
                    TEXTS[langue]["pct_brand"]: f"{100 * total_branded / total_kw:.1f}%" if total_kw > 0 else "0%",
                    TEXTS[langue]["pct_nonbrand"]: f"{100 * total_nonbranded / total_kw:.1f}%" if total_kw > 0 else "0%",
                }
                synthese_df = pd.concat([synthese_df, pd.DataFrame([total_row])], ignore_index=True)

            st.success(TEXTS[langue]["n_lines"].format(len(fusion)))
            # --------------------------------------
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                fusion.to_excel(writer, index=False, sheet_name="KW filtrés")
                synthese_df.to_excel(writer, index=False, sheet_name="Synthese")
                workbook = writer.book
                for sheetname, sheetdata in zip(['KW filtrés', 'Synthese'], [fusion, synthese_df]):
                    worksheet = writer.sheets[sheetname]
                    for col_num, value in enumerate(sheetdata.columns):
                        col_values = sheetdata[value]
                        if col_values.astype(str).str.startswith('http').any():
                            url_format = workbook.add_format({'num_format': '@'})
                            worksheet.set_column(col_num, col_num, None, url_format)
            st.download_button(
                label=TEXTS[langue]["dl_label"],
                data=output.getvalue(),
                file_name=TEXTS[langue]["dl_filename"],
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            # --------------------------------------
            st.subheader("🔎 " + TEXTS[langue]["synth_title"])
            st.dataframe(
                synthese_df,
                use_container_width=True, 
                height=min(600, 60 + 30*len(synthese_df))
            )
            st.dataframe(
                fusion.head(100),
                use_container_width=True,
                height=60 + 35*20
            )

        else:
            st.warning(TEXTS[langue]["no_data"])
else:
    st.info(TEXTS[langue]["info_upload"])
