import streamlit as st
import pandas as pd
import datetime
import os
from datetime import timedelta

# Configuration de la page
st.set_page_config(
    page_title="Gestion Anapath Pro", 
    layout="wide",
    page_icon="🔬"
)

# Style CSS amélioré
def load_css():
    st.markdown("""
    <style>
        .main {
            background-color: #f9f9f9;
            padding: 20px;
        }
        .stButton>button {
            background-color: #2c3e50;
            color: white;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            background-color: #1a252f;
            transform: scale(1.02);
        }
        .status-pending {
            background-color: #fff3cd !important;
        }
        .status-done {
            background-color: #d4edda !important;
        }
        .status-late {
            background-color: #f8d7da !important;
        }
        .status-not-taken {
            background-color: #ffeeba !important;
        }
        .header-box {
            background-color: #2c3e50;
            color: white;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .form-box {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .dataframe {
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True)

load_css()

# Base de données
DB_PATH = "data/anapath_db.csv"
LATE_CASES_PATH = "data/late_cases.csv"

def init_dbs():
    """Initialise les bases de données"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Base principale
    if not os.path.exists(DB_PATH):
        pd.DataFrame(columns=[
            "id", "numero_dossier", "nom", "prenom", "telephone",
            "date_prelevement", "date_reception", "diagnostic", 
            "statut", "pris_par_patient", "commentaires",
            "created_at", "updated_at"
        ]).to_csv(DB_PATH, index=False)
    
    # Cas en retard
    if not os.path.exists(LATE_CASES_PATH):
        pd.DataFrame(columns=[
            "id_anapath", "numero_dossier", "nom", "prenom", 
            "telephone", "diagnostic", "date_declaration", 
            "motif_retard", "actions_prises", "date_updated"
        ]).to_csv(LATE_CASES_PATH, index=False)

def load_db(path):
    try:
        return pd.read_csv(path)
    except:
        return pd.DataFrame()

def save_db(df, path):
    df.to_csv(path, index=False)

def generate_dossier_number():
    """Génère un numéro de dossier unique basé sur la date et un compteur"""
    today = datetime.datetime.now().strftime("%Y%m%d")
    existing_db = load_db(DB_PATH)
    
    if not existing_db.empty:
        # Compter le nombre d'analyses aujourd'hui
        today_analyses = existing_db[existing_db['created_at'].str.startswith(today[:10])]
        counter = len(today_analyses) + 1
    else:
        counter = 1
    
    return f"ANA-{today}-{counter:03d}"

# 1. Enregistrement des anapaths avec diagnostic manuel
def enregistrement():
    st.markdown("<div class='header-box'><h1>📝 Nouvelle Analyse Anatomopathologique</h1></div>", unsafe_allow_html=True)
    
    with st.container():
        with st.form("new_anapath", clear_on_submit=True):
            st.markdown("<div class='form-box'>", unsafe_allow_html=True)
            
            # Génération automatique du numéro de dossier
            dossier_num = generate_dossier_number()
            st.markdown(f"**Numéro de dossier généré:** {dossier_num}")
            
            cols = st.columns(2)
            
            with cols[0]:
                st.subheader("Informations Patient")
                nom = st.text_input("Nom complet*").upper()
                prenom = st.text_input("Prénom*").capitalize()
                telephone = st.text_input("Téléphone*", help="Format: +225 XX XX XX XX")
            
            with cols[1]:
                st.subheader("Détails Analyse")
                date_prelevement = st.date_input("Date prélèvement*", datetime.date.today())
                date_reception = st.date_input("Date réception*", datetime.date.today())
                diagnostic = st.text_area("Diagnostic*", height=100, help="Saisissez le diagnostic complet")
            
            commentaires = st.text_area("Commentaires supplémentaires")
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            if st.form_submit_button("💾 Enregistrer l'analyse", use_container_width=True):
                if not nom or not prenom or not telephone or not diagnostic:
                    st.error("Veuillez remplir tous les champs obligatoires (*)")
                else:
                    new_entry = {
                        "id": len(load_db(DB_PATH)) + 1,
                        "numero_dossier": dossier_num,
                        "nom": nom,
                        "prenom": prenom,
                        "telephone": telephone,
                        "date_prelevement": str(date_prelevement),
                        "date_reception": str(date_reception),
                        "diagnostic": diagnostic,
                        "statut": "En cours",
                        "pris_par_patient": "Non",
                        "commentaires": commentaires,
                        "created_at": str(datetime.datetime.now()),
                        "updated_at": str(datetime.datetime.now())
                    }
                    
                    df = load_db(DB_PATH)
                    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                    save_db(df, DB_PATH)
                    st.success("Analyse enregistrée avec succès!")
                    st.balloons()

# 2. Recherche améliorée - Affiche toutes les analyses par défaut
def recherche():
    st.markdown("<div class='header-box'><h1>🔍 Recherche & Gestion des Analyses</h1></div>", unsafe_allow_html=True)
    
    # Charger toutes les analyses dès l'ouverture
    df = load_db(DB_PATH)
    
    with st.container():
        st.markdown("<div class='form-box'>", unsafe_allow_html=True)
        
        # Filtres avancés
        cols = st.columns([2, 1, 1, 1])
        with cols[0]:
            search_term = st.text_input("Recherche par nom/numéro dossier")
        with cols[1]:
            statut_filter = st.selectbox("Statut analyse", ["Tous", "En cours", "Terminé", "En retard"])
        with cols[2]:
            patient_statut = st.selectbox("Prise par patient", ["Tous", "Oui", "Non"])
        with cols[3]:
            date_filter = st.date_input("Filtrer par date", value=None)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Appliquer les filtres
    if not df.empty:
        if search_term:
            df = df[
                df["numero_dossier"].str.contains(search_term, case=False, na=False) |
                df["nom"].str.contains(search_term, case=False, na=False) |
                df["prenom"].str.contains(search_term, case=False, na=False)
            ]
        
        if statut_filter != "Tous":
            df = df[df["statut"] == statut_filter]
        
        if patient_statut != "Tous":
            df = df[df["pris_par_patient"] == patient_statut]
        
        if date_filter:
            df['date_reception'] = pd.to_datetime(df['date_reception'])
            df = df[df['date_reception'].dt.date == date_filter]
    
    # Affichage des résultats
    if not df.empty:
        # Formatage conditionnel
        def style_row(row):
            styles = []
            for _ in row:
                if row["statut"] == "En retard":
                    styles.append("background-color: #f8d7da")
                elif row["statut"] == "Terminé":
                    styles.append("background-color: #d4edda")
                elif row["pris_par_patient"] == "Non":
                    styles.append("background-color: #fff3cd")
                else:
                    styles.append("")
            return styles
        
        # Afficher le nombre de résultats
        st.markdown(f"**{len(df)} analyses trouvées**")
        
        # Afficher le tableau complet
        st.dataframe(
            df.style.apply(style_row, axis=1),
            use_container_width=True,
            column_order=[
                "numero_dossier", "nom", "prenom", "telephone",
                "date_reception", "diagnostic", "statut",
                "pris_par_patient"
            ],
            hide_index=True,
            height=600
        )
        
        # Gestion du statut
        with st.expander("📝 Mettre à jour le statut", expanded=True):
            selected_id = st.selectbox("Sélectionner une analyse", df["numero_dossier"])
            
            cols = st.columns(2)
            with cols[0]:
                new_status = st.selectbox(
                    "Statut analyse",
                    ["En cours", "Terminé", "En retard"],
                    index=["En cours", "Terminé", "En retard"].index(
                        df[df["numero_dossier"] == selected_id]["statut"].values[0]
                    )
                )
            with cols[1]:
                patient_status = st.radio(
                    "Prise par patient",
                    ["Oui", "Non"],
                    index=0 if df[df["numero_dossier"] == selected_id]["pris_par_patient"].values[0] == "Oui" else 1,
                    horizontal=True
                )
            
            if st.button("💾 Enregistrer les modifications"):
                df.loc[df["numero_dossier"] == selected_id, "statut"] = new_status
                df.loc[df["numero_dossier"] == selected_id, "pris_par_patient"] = patient_status
                df.loc[df["numero_dossier"] == selected_id, "updated_at"] = str(datetime.datetime.now())
                save_db(df, DB_PATH)
                st.success("Statut mis à jour avec succès!")
                st.rerun()
    else:
        st.warning("Aucune analyse trouvée dans le système")

# 3. Déclaration manuelle des retards
def retards():
    st.markdown("<div class='header-box'><h1>⚠️ Gestion des Retards</h1></div>", unsafe_allow_html=True)
    
    with st.container():
        # Formulaire manuel de déclaration
        with st.expander("📝 Nouvelle déclaration de retard", expanded=True):
            with st.form("late_declaration"):
                st.markdown("<div class='form-box'>", unsafe_allow_html=True)
                
                cols = st.columns(2)
                with cols[0]:
                    numero_dossier = st.text_input("Numéro dossier*")
                    nom = st.text_input("Nom patient*").upper()
                    prenom = st.text_input("Prénom patient*").capitalize()
                    telephone = st.text_input("Téléphone*")
                
                with cols[1]:
                    diagnostic = st.text_area("Diagnostic*", height=100)
                    motif_retard = st.selectbox(
                        "Motif du retard*",
                        ["Problème technique", "Retard prélèvement", 
                         "Analyse complexe", "Autre"]
                    )
                
                actions_prises = st.text_area("Actions prises")
                commentaires = st.text_area("Commentaires supplémentaires")
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                if st.form_submit_button("⚠️ Déclarer le retard", use_container_width=True):
                    required_fields = [numero_dossier, nom, prenom, telephone, diagnostic]
                    if not all(required_fields):
                        st.error("Veuillez remplir tous les champs obligatoires (*)")
                    else:
                        # Enregistrement dans la table des retards
                        new_late = {
                            "id_anapath": "",  # sera mis à jour si trouvé
                            "numero_dossier": numero_dossier,
                            "nom": nom,
                            "prenom": prenom,
                            "telephone": telephone,
                            "diagnostic": diagnostic,
                            "motif_retard": motif_retard,
                            "actions_prises": actions_prises,
                            "commentaires": commentaires,
                            "date_declaration": str(datetime.datetime.now()),
                            "date_updated": str(datetime.datetime.now())
                        }
                        
                        # Mise à jour de la base principale si l'analyse existe
                        main_db = load_db(DB_PATH)
                        if not main_db.empty:
                            match = main_db[main_db["numero_dossier"] == numero_dossier]
                            if not match.empty:
                                main_db.loc[main_db["numero_dossier"] == numero_dossier, "statut"] = "En retard"
                                new_late["id_anapath"] = match.iloc[0]["id"]
                                save_db(main_db, DB_PATH)
                        
                        # Sauvegarde dans la table des retards
                        late_cases = load_db(LATE_CASES_PATH)
                        late_cases = pd.concat([late_cases, pd.DataFrame([new_late])], ignore_index=True)
                        save_db(late_cases, LATE_CASES_PATH)
                        
                        st.success("Déclaration de retard enregistrée!")
                        st.balloons()
    
    # Liste des retards
    st.markdown("### 📋 Liste des analyses en retard")
    late_cases = load_db(LATE_CASES_PATH)
    if not late_cases.empty:
        st.dataframe(
            late_cases,
            use_container_width=True,
            column_order=[
                "numero_dossier", "nom", "prenom", "telephone",
                "motif_retard", "date_declaration", "actions_prises"
            ],
            hide_index=True
        )
    else:
        st.info("Aucun retard déclaré pour le moment")

# Menu principal
def main():
    init_dbs()
    
    st.sidebar.title("Menu Principal")
    st.sidebar.markdown("---")
    
    menu = st.sidebar.radio(
        "Navigation",
        ["Enregistrement", "Recherche", "Retards"],
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Version:** 2.0 | **Dernière MAJ:** {datetime.datetime.now().strftime('%d/%m/%Y')}")
    
    if menu == "Enregistrement":
        enregistrement()
    elif menu == "Recherche":
        recherche()
    elif menu == "Retards":
        retards()

if __name__ == "__main__":
    main()