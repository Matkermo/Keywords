import streamlit as st
import pandas as pd
from io import BytesIO
import plotly.express as px
import re

# 💬 Paramètres langues et textes v10
country_flags = {"FR": "🇫🇷", "EN": "🇺🇸"}
LANG_OPTIONS = ['FR 🇫🇷', 'EN 🇺🇸']
LANG_CODES = {'FR 🇫🇷': 'FR', 'EN 🇺🇸': 'EN'}

TEXTS = {
    "FR": {
        "app_title": "🔍 Pré-traitement SEO : Branded & Non-branded 🇫🇷",
        "app_desc": "Chargez plusieurs fichiers SEMrush et vos mots spécifiques pour séparer les mots-clés branded et non-branded.",
        "upload_label": "Fichiers SEMrush (.csv, .xlsx)",
        "min_volume": "Volume minimum",
        "max_kd": "Difficulté KD max (%)",
        "brands_list": "📝 Mots-clés branded",
        "manual_brands": "Entrez vos mots spécifiques (1 par ligne)",
        "brand_file": "📎importe un fichier de mots branded (txt, csv ou xlsx)",
        "run": "Lancer le pré-traitement",
        "synth_title": "Synthèse par source",
        "kw_total": "KW total",
        "kw_brand": "KW branded",
        "kw_nonbrand": "KW non-branded",
        "hard_kd": "↗️ Hard KD",
        "low_volume": "↙️ Low Volume",
        "dl_label": "Télécharger résultats CSV",
        "synth_dl_label": "Télécharger CSV synthèse",
        "dl_filename": "kw_filtrés.csv",
        "n_lines": "Traitement terminé ({:d} lignes)",
        "info_upload": "Veuillez charger au moins un fichier SEMrush.",
        "error_keyword": "Colonne 'Keyword' introuvable ! Colonnes dispo:",
        "error_parse": "Erreur de chargement :",
        "no_data": "Aucune donnée exploitable. Vérifiez vos fichiers.",
        "total": "TOTAL",
        "true": "VRAI",
        "false": "FAUX",
        "company": "Compagnie",
        "raw_data": "🔍 Données brutes",
        "branded_analysis": "Analyse Branded"
    },
    "EN": {
        "app_title": "🔍 SEO Pre-processing: Branded & Non-branded 🇺🇸",
        "app_desc": "Upload one or more SEMrush files and your brands to separate branded and non-branded keywords.",
        "upload_label": "SEMrush files (.csv, .xlsx)",
        "min_volume": "Minimum volume",
        "max_kd": "Max KD (%)",
        "brands_list": "📝 Brand keywords",
        "manual_brands": "Enter specific words/brands (one per line)",
        "brand_file": "📎 import a list of branded keywords (txt, csv, xlsx)",
        "run": "Run pre-processing",
        "synth_title": "Summary per source",
        "kw_total": "KW total",
        "kw_brand": "KW branded",
        "kw_nonbrand": "KW non-branded",
        "hard_kd": "↗️ Hard KD",
        "low_volume": "↙️ Low Volume",
        "dl_label": "Download CSV results",
        "dl_model": "Download branded keyword model",
        "synth_dl_label": "Download CSV summary",
        "dl_filename": "filtered_kw.csv",
        "n_lines": "Done ({:d} rows processed)",
        "info_upload": "Please upload at least one SEMrush file.",
        "error_keyword": "'Keyword' column not found! Available columns:",
        "error_parse": "Loading error:",
        "no_data": "No usable data. Check your files.",
        "total": "TOTAL",
        "true": "TRUE",
        "false": "FALSE",
        "company": "Company",
        "raw_data": "🔍 Raw Data",
        "branded_analysis": "Branded Analysis"
    }
}

# Ajouter les premiers mots-clés
initial_brands = [
    "ut", "abudhabi", "francia", "hawaii", "korea", "maroc", "MN", "MS", "NC", "ND",
    "NH", "NJ", "NM", "okc", "SD", "slb", "thailande", "UK", "VA", "VT", "WA", "aberdeen",
    "abidjan", "abrdn", "abu dhabi", "Africa", "africain", "afrique", "AK", "Alabama",
    "Alaska", "Albany", "algeria", "algerie", "algérie", "alibaba", "Allemagne", "amen",
    "america", "american", "amerique latine", "anchorage", "anderson", "angeles", "angola",
    "Annapolis", "antonio", "appleton", "aquitaine", "arabes", "arabia", "arabian", "argentina",
    "Arizona", "Arkansas", "asia", "Atlanta", "Augusta", "Austin", "australia", "australie",
    "AZ", "azerbaijan", "bahrain", "bakersfield", "baku", "bangkok", "barcelone", "baskerville",
    "Baton Rouge", "Belgique", "belgium", "bergen", "Bismarck", "bismart", "bogota", "Boise",
    "bordeaux", "Boston", "brazil", "bresil", "brésil", "brownsville", "CA", "calgary",
    "California", "californie", "cameroun", "canada", "canadian", "cardiff", "career",
    "Carolina", "Carson City", "carte du monde", "Charleston", "Cheyenne", "chicago", "chili",
    "chine", "city", "clarksville", "CO", "cologne", "colombia", "colombie", "colombus",
    "Colorado", "Columbie", "Columbus", "Concord", "Connecticut", "continent", "corée du sud",
    "CT", "cuba", "Dakota", "dallas", "danemark", "Delaware", "denmark", "Denver", "Des Moines",
    "dickinson", "d'ivoire", "Dover", "dubai", "dubois", "dutch", "eastern", "eclispe", 
    "edmonton", "egypt", "egypte", "eiffel", "eldridge", "emirates", "emirats", "england",
    "Espagne", "espasgne", "Florida", "forth worth", "Frankfort", "gabon", "gayana", "Georgia",
    "german", "germany", "ghana", "guyana", "halliburton", "halliburton", "Hampshire", "Harrisburg",
    "Hartford", "Hawaii", "Helena", "hk", "holland", "hong", "hong kong", "Honolulu", "houma",
    "houston", "huston","iberia", "Idaho", "illinois", "inde", "india", "Indiana", "Indianapolis",
    "indienne", "indonesia", "indonésia", "indonesie", "indonésie", "Iowa", "iran", "irelande",
    "islande", "istanbul", "italia", "italian", "Italie", "ivoire", "Jackson", "jacksonville", 
    "japan", "japon", "Jefferson City", "Jersey", "Juneau", "Kansas", "katy", "Kentucky", "kingdom", 
    "kinshasa", "korea", "kristiansand", "KS", "kuwait", "KY", "lafayette", "lagos", "Lansing", 
    "liban", "l'ile maurice", "Lincoln", "lisbonne", "Little Rock", "london", "londres", "Louisiana", 
    "luxembour", "lyon", "lysaker", "madagascar", "Madison", "madrid", "Maine", "malaisie", 
    "mallard", "manchester", "mangascar", "marocco", "maroco", "marseille", "Maryland", 
    "Massachusetts", "maurice", "MD", "Mexico", "Mexique", "Michigan", "midland", "minesota", 
    "minneapolis", "Minnesota", "Mississippi", "Missouri", "Montana", "Montgomery", "Montpelier", 
    "montreal", "montréal", "Nashville", "ndt", "Nebraska", "nederland", "Nevada", "new mexico", 
    "new york", "New zeland", "nigeria", "nigéria", "norvege", "norvège", "norway", 
    "nouvelle zelande", "nouvelle zélande", "NOV", "NV", "NY", "nyc", "nz", "odessa", "Ohio", 
    "okc", "Oklahoma", "olso", "Olympia", "oman", "Oregon", "oslo", "pays bas", "pays bs", 
    "pays nordiques", "Pennsylvania", "phoenix", "Portugal", "Providence", "qatar", "Raleigh", 
    "recruite", "recruiters", "recruitment", "republique", "Rhode Island", "Richmond", 
    "rocheuses", "romania", "Sacramento", "Saint Paul", "salary", "Salem", "salinas", 
    "Salt Lake City", "san francisco", "Santa Fe", "saudi", "scandinaves", "scotland", "seattle", 
    "seoul", "serbi", "serbie", "shreveport", "singapore", "spain", "Springfield", "stonehouse", 
    "suede", "suède", "suisse", "sydney", "syracuse", "tabasco", "Tallahassee", "techèque", 
    "Tennessee", "Texas", "thailand", "thaïlande", "thaillande", "TN", "Topeka", "toulouse", 
    "Trenton", "trinidad", "tucson", "tulsa", "tunisie", "turkey", "TX", "uk", "united kingdom", 
    "united state", "united states", "us", "us", "usa", "Utah", "vancouver", "veitman", 
    "ventana", "veracruz", "Vermont", "versailles", "vienna", "vietnam", "virginia", 
    "w y", "w.y.", "wa", "waco", "Washington", "West Virginia", "wilcrest", "williston", 
    "Wisconsin", "WV", "WY", "Wyoming", "York", "zagreb"
]

def is_branded_kw(keyword, brand_set):
    # Convertir le mot-clé en minuscules
    lower_keyword = str(keyword).lower()
    
    # Vérification pour chaque marque dans le set
    for brand in brand_set:
        brand = str(brand).strip().lower()
        
        # Si la marque a moins de 3 caractères, vérification avec match exact
        if len(brand) <= 3:
            # Utiliser une regex avec \b pour match exact du mot complet
            if re.search(r'\b' + re.escape(brand) + r'\b', lower_keyword):
                return True
        else:
            # Pour les marques plus longues, on vérifie si la marque est présente dans le texte
            if brand in lower_keyword:
                return True
    
    return False


# Configuration Streamlit
st.set_page_config(layout="wide")

# Langue et barre latérale
col1, colspace, col2 = st.columns([6, 2, 1])
with col2:
    select_lang = st.selectbox("", LANG_OPTIONS, label_visibility='collapsed')
langue = LANG_CODES[select_lang]

# Titre et description
st.markdown(f"<h3 style='margin-top: 0;'>{TEXTS[langue]['app_title']}</h3>", unsafe_allow_html=True)
st.markdown(TEXTS[langue]["app_desc"])

# Sidebar
with st.sidebar:
    st.header("🖇️ Imports SEMrush")
    uploaded_files = st.file_uploader(TEXTS[langue]["upload_label"], accept_multiple_files=True)
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        min_volume = st.number_input(TEXTS[langue]["min_volume"], min_value=0, value=100, step=50)

    with col2:
        max_kd = st.number_input(TEXTS[langue]["max_kd"], min_value=0, max_value=100, value=50, step=10)

    st.markdown("---")
    st.write(TEXTS[langue]["brands_list"])
    brand_input = st.text_area(TEXTS[langue]["manual_brands"], height=100)
    brand_file = st.file_uploader(TEXTS[langue]["brand_file"], type=["txt", "xlsx"])
    run_btn = st.button(TEXTS[langue]["run"])

# Fonction pour créer le modèle de fichier
def create_model_file():
    df = pd.DataFrame({
        "Branded Keyword": initial_brands  # Ajout des mots-clés initiaux
    })
    return df

# Fonction de téléchargement du modèle encapsulée
def download_model():
    # Création du modèle de fichier
    model_df = create_model_file()
    buffer = BytesIO()
    model_df.to_excel(buffer, index=False)
    buffer.seek(0)

    # Utiliser un gestionnaire de contexte pour la barre latérale
    with st.sidebar:
        st.subheader(TEXTS[langue]["dl_model"] if langue == "EN" else "Télécharger le Modèle de Branded Keywords")
        st.download_button(
            label=TEXTS[langue]["dl_label"] if langue == "FR" else "Download Model",
            data=buffer,
            file_name="branded_keywords_model.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_model"
        )

# Appel de la fonction pour télécharger le modèle
download_model()

# Génération dynamique des couleurs
default_colors = {
    "synthese": ["#4CAF50", "#FF9800", "#2196F3", "#F44336"],
}

# Processus d'importation
if uploaded_files and run_btn:
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

            # Nom du fichier (sans extension et avec première lettre en majuscule)
            file_name = upl.name.rsplit('.', 1)[0].title()  # Enlève l'extension et met en majuscule
            df['Fichier'] = file_name  # Utiliser le nom sans extension

            # Ajout de la colonne de mots-clés branded
            branded_col = []  # On définit la liste vide ici pour éviter l'erreur

            # On boucle sur chaque mot-clé dans le DataFrame
            for kw in df['Keyword']:
                result = is_branded_kw(kw, brand_set)
                # Affichage pour comprendre où ça pose problème
                print(f"Keyword: {kw} => is_branded_kw: {result}")
                # Ajout du résultat dans la liste branded_col
                branded_col.append(TEXTS[langue]["true"] if result else TEXTS[langue]["false"])

            # On ajoute la colonne 'Branded'
            df['branded'] = branded_col

            # Ajout de la colonne des raisons
            reason_col = []

            for _, row in df.iterrows():
                if row['branded'] == TEXTS[langue]["true"]:
                    # Trouver le mot de marque correspondant (plus rigoureux avec regex)
                    keyword_words = re.findall(r"\b[\w'-]+\b", row['Keyword'].lower())
                    branded_word = next(
                        (
                            brand for brand in brand_set
                            if (
                                (len(brand) <= 3 and brand.lower() in keyword_words) or
                                (len(brand) > 3 and brand.lower() in row['Keyword'].lower())
                            )
                        ),
                        None
                    )
                    reasoning = branded_word if branded_word else "Unknown Brand"
                    reason_col.append(reasoning)
                elif row['Keyword Difficulty'] > max_kd:
                    reason_col.append("Hard KD")
                elif row['Search Volume'] < min_volume:
                    reason_col.append("Low Volume")
                else:
                    reason_col.append("non_Branded")

            # Insertion de la colonne à la bonne position
            idx_kw = df.columns.get_loc('Keyword')
            insert_pos = min(idx_kw + 2, len(df.columns))
            df.insert(insert_pos, 'reason', reason_col)

            # Ajout de la colonne de catégorie LV/HardKD
            category_col = []
            for _, row in df.iterrows():
                if row['Search Volume'] < min_volume:
                    category_col.append("Low Volume")
                elif row['Keyword Difficulty'] > max_kd:
                    category_col.append("Hard KD")
                else:
                    category_col.append("")
            df.insert(idx_kw + 3, 'Category', category_col)

            mask_category_empty = (df['Category'] == "")
            mask_branded = df['branded'] == TEXTS[langue]["true"]
            mask_nonbranded = df['branded'] == TEXTS[langue]["false"]

            n_total = len(df)
            n_kwbrand = ((mask_category_empty) & (mask_branded)).sum()
            n_kwnonbrand = ((mask_category_empty) & (mask_nonbranded)).sum()
            n_hardkd = (df['Category'] == "Hard KD").sum()
            n_lowvol = (df['Category'] == "Low Volume").sum()

            synthese.append({
                "Fichier": file_name,
                TEXTS[langue]["kw_total"]: n_total,
                TEXTS[langue]["kw_brand"]: n_kwbrand,
                TEXTS[langue]["kw_nonbrand"]: n_kwnonbrand,
                TEXTS[langue]["hard_kd"]: n_hardkd,
                TEXTS[langue]["low_volume"]: n_lowvol,
            })

            all_processed.append(df)

            st.write(f"✅ {upl.name}: {n_total} lignes chargées")
        except Exception as e:
            st.error(f"{TEXTS[langue]['error_parse']} {e}")
        progress.progress(int(100 * (i + 1) / len(uploaded_files)))

    if all_processed:
        fusion = pd.concat(all_processed, ignore_index=True)
        synthese_df = pd.DataFrame(synthese)

        # Ajout de la ligne totale sans pourcentages
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
            }
            synthese_df = pd.concat([synthese_df, pd.DataFrame([total_row])], ignore_index=True)

        # Renommer la colonne "Fichier"
        synthese_df.rename(columns={"Fichier": TEXTS[langue]["company"]}, inplace=True)

        st.success(TEXTS[langue]["n_lines"].format(len(fusion)))

        # Affichage par Onglets
        tabs = st.tabs(
            ["📊 " + TEXTS[langue]["synth_title"]] +
            [fname.split('.')[0] for fname in fusion['Fichier'].unique()] +
            [TEXTS[langue]["branded_analysis"], TEXTS[langue]["raw_data"]]
        )

        # Onglet Synthèse Globale
        with tabs[0]:
            st.subheader("🔎 " + TEXTS[langue]["synth_title"])
            st.dataframe(synthese_df, use_container_width=True, height=min(600, 60 + 30 * len(synthese_df)))

            # Bouton de téléchargement pour la synthèse
            @st.fragment
            def download_synth_data():
                st.download_button(
                    label=TEXTS[langue]["synth_dl_label"],
                    icon="📥",
                    data=synthese_df.to_csv(index=False),
                    file_name="synthese.csv",
                    mime="text/csv",
                    use_container_width=True,
                    disabled=synthese_df.empty
                )

            download_synth_data()

            # Graphiques
            synth_global_row = synthese_df[synthese_df[TEXTS[langue]["company"]] == TEXTS[langue]["total"]]
            if not synth_global_row.empty:
                colpie, colbar = st.columns(2)

                # Graphique en camembert
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
                    fig1.update_traces(textinfo='percent+label')  # Affiche pourcentage + label
                    st.plotly_chart(fig1, use_container_width=True)

                # Graphique en barres
                with colbar:
                    fig2 = px.bar(
                        x=labels,
                        y=values,
                        color=labels,
                        color_discrete_sequence=colors,
                        title="Distribution globale"
                    )
                    fig2.update_traces(texttemplate='%{y}', textposition='outside')  # Affiche uniquement les valeurs
                    st.plotly_chart(fig2, use_container_width=True)

        # Onglet par fichier avec graphiques
        for idx in range(1, len(tabs) - 2):
            fname = fusion['Fichier'].unique()[idx - 1]  # Récupère le nom du fichier actuel
            with tabs[idx]:
                st.subheader(f"Analyse pour {fname}")

                # Filtrer les données du fichier actuel
                file_data = fusion[fusion["Fichier"] == fname]
                n_total = len(file_data)

                # Créer les masques
                mask_category_empty = (file_data['Category'] == "")
                mask_branded = file_data['branded'] == TEXTS[langue]["true"]
                mask_nonbranded = file_data['branded'] == TEXTS[langue]["false"]

                # Calculs
                n_kwbrand = ((mask_category_empty) & (mask_branded)).sum()
                n_kwnonbrand = ((mask_category_empty) & (mask_nonbranded)).sum()
                n_hardkd = (file_data['Category'] == "Hard KD").sum()
                n_lowvol = (file_data['Category'] == "Low Volume").sum()

                # Créer un dictionnaire des résultats
                results = {
                    "Compagnie": fname,
                    "Total": n_total,
                    "Brand": n_kwbrand,
                    "Non-brand": n_kwnonbrand,
                    "Hard KD": n_hardkd,
                    "Low Volume": n_lowvol,
                }

                # Ajouter à la synthèse pour affichage ultérieur
                synthese.append(results)

                # Créer un DataFrame pour l'affichage
                df_synthese = pd.DataFrame([results])  # Utilisation de [results] pour créer une seule ligne

                # Affichage des résultats dans un tableau
                st.dataframe(df_synthese, use_container_width=True)  # Affichage de manière adaptée

                # Graphiques
                colpie, colbar = st.columns(2)
                with colpie:
                    values = [n_kwnonbrand, n_kwbrand, n_hardkd, n_lowvol]
                    labels = [TEXTS[langue]["kw_nonbrand"], TEXTS[langue]["kw_brand"], TEXTS[langue]["hard_kd"], TEXTS[langue]["low_volume"]]
                    colors = default_colors["synthese"]
                    fig3 = px.pie(
                        names=labels,
                        values=values,
                        color=labels,
                        color_discrete_sequence=colors,
                        title=f"Répartition globale des mots-clés pour {fname}"
                    )
                    fig3.update_traces(textinfo='percent+label')  # Affiche pourcentage + label

                    # Ajustement de la taille et des marges
                    fig3.update_layout(
                        height=550,   # Ajuste la hauteur
                        width=825,    # Ajuste la largeur
                        margin=dict(t=50, b=20, l=20, r=20)  # Marges autour du graphique
                    )

                    st.plotly_chart(fig3, use_container_width=True)

                with colbar:
                    fig4 = px.bar(
                        x=labels,
                        y=values,
                        color=labels,
                        color_discrete_sequence=colors,
                        title=f"Distribution globale pour {fname}"
                    )
                    fig4.update_traces(texttemplate='%{y}', textposition='outside')  # Affiche uniquement les valeurs
                    # Ajustement de la taille et des marges
                    fig4.update_layout(
                        height=550,   # Ajuste la hauteur
                        width=500,    # Ajuste la largeur
                        margin=dict(t=50, b=20, l=20, r=20)  # Marges autour du graphique
                    )

                    st.plotly_chart(fig4, use_container_width=True)

                # Affichage des 20 premières lignes
                st.write("### Aperçu des 20 premières lignes")
                st.dataframe(file_data.head(20), use_container_width=True)

        # Onglet Analyse Branded
        with tabs[-2]:
            st.write(f"### {TEXTS[langue]['branded_analysis']} sans applications de seuils KD & Volume search" if langue == "FR" else f"### {TEXTS[langue]['branded_analysis']} without applying KD & Volume Search")

            summary_data = fusion.groupby('Fichier').agg(
                KW_branded=('branded', lambda x: (x == TEXTS[langue]["true"]).sum()),
                KW_nonbranded=('branded', lambda x: (x == TEXTS[langue]["false"]).sum())
            ).reset_index()

            # Calculer les totaux
            total_branded = summary_data['KW_branded'].sum()
            total_nonbranded = summary_data['KW_nonbranded'].sum()

            # Créer une ligne de total
            total_row = pd.DataFrame({
                'Fichier': ['TOTAL'],
                'KW_branded': [total_branded],
                'KW_nonbranded': [total_nonbranded]
            })

            # Ajouter cette ligne au DataFrame
            df_branded_analysis = pd.concat([summary_data, total_row], ignore_index=True).rename(columns={'Fichier': TEXTS[langue]["company"]})

            # Affichage dans un tableau
            st.dataframe(df_branded_analysis, use_container_width=True)

            # Graphique en camembert
            pie_values = [total_nonbranded, total_branded]
            pie_labels = ['Non-Branded', 'Branded']

            fig_pie = px.pie(
                names=pie_labels,
                values=pie_values,
                color=pie_labels,
                color_discrete_sequence=["#FF9800", "#4CAF50"],  # Couleurs pour Non-Branded et Branded
                title="Répartition des Mots-Clés Branded et Non-Branded"
            )

            # Ajustements pour afficher les pourcentages à l'intérieur des parts
            fig_pie.update_traces(textinfo='percent+label')  # Affiche pourcentage + label
            st.plotly_chart(fig_pie, use_container_width=True)

    # Onglet données brutes
    with tabs[-1]:
        st.subheader(TEXTS[langue]["raw_data"])
        st.write("Aperçu des données traitées :")

        # Sélectionner et réorganiser les colonnes pour l'affichage
        ordered_display_columns = ["Keyword", "Source", "branded", "reason", "Category", "Position", "Previous position", "Search Volume", "Keyword Difficulty", "URL"]

        # Vérifier les colonnes disponibles pour l'affichage
        if set(ordered_display_columns).issubset(fusion.columns):
            fusion_display_ordered = fusion[ordered_display_columns]
        else:
            st.warning("Certaines colonnes d'affichage ne sont pas présentes dans le DataFrame.")
            fusion_display_ordered = fusion

        st.dataframe(fusion_display_ordered, use_container_width=True)

        # Fonction de préparation des données pour le téléchargement
        @st.cache_data
        def prepare_download_data():
            # Sélectionner toutes les colonnes pour le téléchargement dans l'ordre souhaité
            ordered_download_columns = ["Keyword", "Source", "branded", "reason", "Category", "Position", "Previous position", "Search Volume", "Keyword Difficulty", "URL", "CPC", "Traffic", "Traffic (%)", "Traffic Cost", "Competition", "Number of Results", "Trends", "Timestamp", "SERP Features by Keyword", "Keyword Intents", "Position Type", "Fichier"]
            
            return fusion[ordered_download_columns].to_csv(index=False)

        # Fonction de téléchargement encapsulée avec st.fragment
        @st.fragment
        def download_data(page_name: str) -> None:
            page_name_better = page_name.replace("_", " ").capitalize()
            st.download_button(
                label=f"Télécharger les données de {page_name_better} au format CSV",
                icon="📥",
                data=prepare_download_data(),  # Utiliser la fonction préparée
                file_name=f"{page_name}.csv",
                mime="text/csv",
                use_container_width=True,
                disabled=fusion.empty
            )

        # Appel de la fonction de téléchargement avec un nom de page pertinent
        download_data("données_brutes")

        # Avertissement si les données sont vides
        if fusion.empty:
            st.warning(TEXTS[langue]["no_data"])
