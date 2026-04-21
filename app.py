import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
 
# ─────────────────────────────────────────────
# CONFIGURATION DE LA PAGE
# ─────────────────────────────────────────────
st.set_page_config(page_title="HOSPITAL ANALYTICS • PRO", layout="wide")
 
st.markdown("""
<style>
/* Fond principal */
.stApp {
    background: radial-gradient(circle at center, #1a237e 0%, #0d1117 100%) !important;
    color: white !important;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
 
/* Grand titre */
.huge-title {
    font-size: 72px;
    font-weight: 800;
    color: white;
    line-height: 1.1;
    margin: 50px 0 20px 20px;
    text-shadow: 0 0 15px rgba(255,255,255,0.3);
    white-space: nowrap;
}
 
/* Sidebar */
[data-testid="stSidebar"] {
    background-color: rgba(13,17,23,0.8) !important;
    border-right: 1px solid rgba(0,201,255,0.3);
    backdrop-filter: blur(10px);
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p {
    font-size: 18px !important;
    font-weight: 700 !important;
    color: #fffff !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}
 
/* Boutons */
.stButton > button {
    background: linear-gradient(135deg, #00C9FF 0%, #92FE9D 100%) !important;
    color: #0d1117 !important;
    border: none !important;
    border-radius: 5px !important;
    font-weight: bold !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.stButton > button:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 0 15px rgba(0,201,255,0.7);
}
 
/* Cards */
.data-card {
    background-color: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 15px;
}
           
/* Labels des champs de formulaire */
.stTextInput label,
.stNumberInput label,
.stMultiSelect label {
    color: #000000 !important;
    font-weight: 900 !important;
}
</style>
""", unsafe_allow_html=True)
 
# ─────────────────────────────────────────────
# BASE DE DONNÉES
# ─────────────────────────────────────────────
DB_PATH = "medical_system_v3.db"
 
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                nom              TEXT,
                age              INTEGER,
                tel              TEXT,
                adresse          TEXT,
                maladie_detectee TEXT,
                certitude        REAL
            )
        """)
        conn.commit()
 
init_db()
 
def save_patient(nom, age, tel, adresse, maladie, certitude):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO patients VALUES (?,?,?,?,?,?)",
            (nom, age, tel, adresse, maladie, certitude)
        )
        conn.commit()
 
def load_patients():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql(
            "SELECT nom, age, tel, adresse, maladie_detectee, certitude FROM patients",
            conn
        )
 
def delete_all_patients():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM patients")
        conn.commit()
 
# ─────────────────────────────────────────────
# MOTEUR DE DIAGNOSTIC
# ─────────────────────────────────────────────
MALADIES_DB = {
    "Paludisme":             ["Fièvre", "Frissons", "Maux de tête", "Courbatures"],
    "Typhoïde":              ["Douleurs abdominales", "Fatigue extrême", "Perte d'appétit", "Diarrhée"],
    "VIH/SIDA":              ["Sueurs nocturnes", "Éruptions cutanées", "Ganglions gonflés", "Perte de poids"],
    "Diabète":               ["Soif intense", "Urines fréquentes", "Vision floue", "Faim excessive"],
    "Infection Respiratoire":["Toux", "Nez bouché", "Difficulté respiratoire", "Maux de gorge"],
}
 
ALL_SYMPTOMS = sorted({s for symptoms in MALADIES_DB.values() for s in symptoms})
 
def diagnostiquer(symptomes_selectionnes):
    """Retourne (maladie, taux) ou (None, 0) si aucune correspondance."""
    scores = {
        maladie: len(set(symptomes_selectionnes) & set(sympts)) / len(sympts)
        for maladie, sympts in MALADIES_DB.items()
    }
    maladie = max(scores, key=scores.get)
    taux = scores[maladie] * 100
    return (maladie, taux) if taux > 0 else (None, 0)
 
# ─────────────────────────────────────────────
# NAVIGATION
# ─────────────────────────────────────────────
PAGES = [
    "🏠 Tableau de Bord",
    "📝 Nouveau Diagnostic",
    "📊 Analyses Statistiques",
    "💾 Gestion des Données",
]
 
st.sidebar.markdown("## NAVIGATION")
page = st.sidebar.radio("", PAGES, key="nav_radio")
 
# ─────────────────────────────────────────────
# PAGE 1 : TABLEAU DE BORD
# ─────────────────────────────────────────────
if page == PAGES[0]:
    col1, col2 = st.columns([2, 3])
 
    with col1:
        st.markdown(
            '<div class="huge-title">SYSTÈME<br>DE COLLECTE<br>DE DONNÉES</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='font-size:1.2em; opacity:0.8; margin-left:20px;'>"
            "Plateforme de collecte  et de Diagnostic de données ."
            "</p>",
            unsafe_allow_html=True
        )
 
 
# ─────────────────────────────────────────────
# PAGE 2 : NOUVEAU DIAGNOSTIC
# ─────────────────────────────────────────────
elif page == PAGES[1]:
    st.markdown("## 📋 Fiche de Collecte et Analyse des Symptômes")
    st.markdown("---")
 
    with st.form("diagnostic_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nom     = st.text_input("Nom complet du patient *")
            age     = st.number_input("Âge", min_value=0, max_value=110, value=30)
        with col2:
            tel     = st.text_input("Téléphone")
            adresse = st.text_input("Adresse complète *")
 
        st.markdown("### 🔍 Sélectionnez les symptômes")
        symptomes = st.multiselect("Cochez les symptômes observés :", ALL_SYMPTOMS)
 
        submitted = st.form_submit_button("LANCER L'ANALYSE ET SAUVEGARDER")
 
    if submitted:
        errors = []
    
    if not nom.strip():
        errors.append("❌ Le nom du patient est obligatoire.")
    if not adresse.strip():
        errors.append("❌ L'adresse est obligatoire.")
    if not symptomes:
        errors.append("❌ Veuillez sélectionner au moins un symptôme.")
    if age == 0:
        errors.append("❌ L'âge doit être supérieur à 0.")

    if errors:
        for err in errors:
            st.error(err)
    else:
        maladie, taux = diagnostiquer(symptomes)
        if maladie:
            st.success(f"### DIAGNOSTIC PROBABLE : **{maladie.upper()}**")
            st.write(f"Taux de concordance : **{taux:.0f} %**")
            save_patient(nom.strip(), age, tel.strip(), adresse.strip(), maladie, taux)
            st.balloons()
        else:
            st.warning("⚠️ Aucune maladie correspondante trouvée.")
# ─────────────────────────────────────────────
# PAGE 3 : ANALYSES STATISTIQUES
# ─────────────────────────────────────────────
elif page == PAGES[2]:
    st.markdown("## 📊 Analyse Descriptive de la Base de Données")
    st.markdown("---")
 
    df = load_patients()
 
    if df.empty:
        st.info("Aucune donnée disponible. Commencez par enregistrer un patient.")
    else:
        col1, col2 = st.columns(2)
 
        with col1:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            fig1 = px.pie(
                df, names="maladie_detectee", hole=0.5,
                title="Répartition des Diagnostics Probables",
                color_discrete_sequence=px.colors.sequential.Agsunset
            )
            fig1.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white"
            )
            st.plotly_chart(fig1, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
 
        with col2:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            fig2 = px.histogram(
                df, x="age", color="maladie_detectee",
                title="Distribution par Tranche d'Âge",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="white"
            )
            st.plotly_chart(fig2, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
 
        st.markdown("#### Détails complets de la base")
        st.dataframe(df, use_container_width=True)
 
# ─────────────────────────────────────────────
# PAGE 4 : GESTION DES DONNÉES
# ─────────────────────────────────────────────
elif page == PAGES[3]:
    st.markdown("## 💾 Archivage et Exportation CSV")
    st.markdown("---")
 
    df = load_patients()
 
    if df.empty:
        st.info("Aucune donnée à exporter pour le moment.")
    else:
        csv_data = df.to_csv(index=False).encode("utf-8")
 
        st.download_button(
            label="📥 TÉLÉCHARGER TOUTE LA BASE (CSV)",
            data=csv_data,
            file_name="archives_medicales.csv",
            mime="text/csv"
        )
 
        st.markdown("<br><br>---", unsafe_allow_html=True)
 
        if st.button("🗑️ SUPPRIMER TOUTES LES DONNÉES (ADMIN ONLY)"):
            delete_all_patients()
            st.warning("Toutes les données ont été effacées.")
            st.rerun()
 
