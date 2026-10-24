import streamlit as st
import requests
import json

# Configuration de la page
st.set_page_config(
    page_title="Système Multi-Agents Médical",
    page_icon="🩺",
    layout="centered"
)

# Injection de styles CSS sur mesure pour un rendu premium
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Inter:wght@300;400;600&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #1e1b4b 100%);
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif;
    }
    
    .header-title {
        background: linear-gradient(to right, #3b82f6, #8b5cf6, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    
    .header-subtitle {
        text-align: center;
        color: #9ca3af;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    .academic-banner {
        background-color: rgba(245, 158, 11, 0.1);
        border: 1px solid #f59e0b;
        color: #f59e0b;
        padding: 12px;
        border-radius: 8px;
        text-align: center;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
    }
    
    .glass-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 10px 30px 0 rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(12px);
        margin-bottom: 1.5rem;
    }
    
    .red-flag-alert {
        background: rgba(220, 38, 38, 0.15);
        border: 1.5px solid #ef4444;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 1.5rem;
        color: #f87171;
    }
    
    .step-indicator {
        font-size: 0.85rem;
        font-weight: 600;
        color: #a78bfa;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    
    .q-bubble {
        background: rgba(59, 130, 246, 0.15);
        border-left: 4px solid #3b82f6;
        padding: 12px 16px;
        border-radius: 0 12px 12px 0;
        margin-bottom: 1rem;
        font-style: italic;
    }
    
    .a-bubble {
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid #10b981;
        padding: 12px 16px;
        border-radius: 0 12px 12px 0;
        margin-bottom: 1.5rem;
    }
    
    .footer-note {
        text-align: center;
        color: #6b7280;
        font-size: 0.8rem;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# URL du Backend FastAPI
API_URL = st.sidebar.text_input("URL Backend API", value="http://localhost:8000")

# Initialisation de l'état de session Streamlit
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "state_data" not in st.session_state:
    st.session_state.state_data = {}

# En-tête de l'application
st.markdown('<div class="header-title">Orientation Clinique IA</div>', unsafe_allow_html=True)
st.markdown('<div class="header-subtitle">Système multi-agents médical avec LangGraph</div>', unsafe_allow_html=True)
st.markdown('<div class="academic-banner">⚠️ PROJET ACADÉMIQUE : Ce système ne remplace pas une consultation médicale et ne produit aucun diagnostic définitif.</div>', unsafe_allow_html=True)

# Fonction pour réinitialiser la consultation
def reset_consultation():
    st.session_state.thread_id = None
    st.session_state.current_question = None
    st.session_state.state_data = {}
    st.rerun()

# Récupération de l'état à jour depuis l'API si un thread_id existe
if st.session_state.thread_id:
    try:
        response = requests.get(f"{API_URL}/consultation/{st.session_state.thread_id}")
        if response.status_code == 200:
            st.session_state.state_data = response.json()
        else:
            st.sidebar.error("Impossible de récupérer l'état sur le serveur.")
    except Exception as e:
        st.sidebar.error(f"Erreur de connexion avec l'API : {e}")

# Routage des écrans selon le statut
status = st.session_state.state_data.get("status", "none")

# --- ÉCRAN 1 : Saisie du Cas Patient ---
if not st.session_state.thread_id or status == "created" or status == "none":
    st.markdown('<div class="step-indicator">Étape 1 : Saisie du Cas Initial</div>', unsafe_allow_html=True)
    st.markdown("### Décrivez la situation clinique initiale")
    
    # Scénarios de tests rapides pour faciliter la démonstration
    st.write("**Scénarios prédéfinis pour le test académique :**")
    col1, col2, col3 = st.columns(3)
    
    case_example = ""
    with col1:
        if st.button("Cas 1 : Bénin (Toux/Rhume)", use_container_width=True):
            case_example = "Patient avec toux légère, nez qui coule, fatigue modérée depuis 2 jours."
    with col2:
        if st.button("Cas 2 : Grave (Urgences)", use_container_width=True):
            case_example = "Patient avec douleur thoracique, difficulté respiratoire et fièvre élevée (39.5°C)."
    with col3:
        if st.button("Cas 3 : Bénin (Effort)", use_container_width=True):
            case_example = "Patient avec fatigue légère après effort physique intense, sans fièvre ni douleur."
            
    # Zone de texte principale
    patient_case_input = st.text_area(
        "Symptômes, antécédents ou contexte général :",
        value=case_example if case_example else "",
        placeholder="Saisissez la description du cas patient ici...",
        height=150
    )
    
    if st.button("Démarrer la consultation 🚀", type="primary", use_container_width=True):
        if not patient_case_input.strip():
            st.warning("Veuillez saisir une description avant de démarrer.")
        else:
            with st.spinner("Initialisation de la session multi-agents..."):
                try:
                    res = requests.post(
                        f"{API_URL}/consultation/start",
                        json={"patient_case": patient_case_input}
                    )
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state.thread_id = data["thread_id"]
                        st.session_state.current_question = data["current_question"]
                        st.session_state.state_data = data["state"]
                        st.success("Consultation initialisée avec succès !")
                        st.rerun()
                    else:
                        st.error(f"Erreur du backend : {res.text}")
                except Exception as e:
                    st.error(f"Erreur lors de la connexion au serveur API : {e}")

# --- ÉCRAN 2 : Questions / Réponses Patient ---
elif status in ["started", "running", "waiting_for_patient"]:
    st.markdown('<div class="step-indicator">Étape 2 : Échanges avec le Patient</div>', unsafe_allow_html=True)
    
    questions = st.session_state.state_data.get("questions", [])
    answers = st.session_state.state_data.get("answers", [])
    q_count = len(questions)
    a_count = len(answers)
    
    # Affichage de la progression
    st.write(f"**Progression de l'entretien : Question {q_count} / 5**")
    st.progress(min(q_count / 5.0, 1.0))
    
    # Historique des échanges précédents
    if a_count > 0:
        with st.expander("Consulter l'historique des échanges", expanded=False):
            for i in range(a_count):
                st.markdown(f"<div class='q-bubble'>Q{i+1} : {questions[i]}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='a-bubble'>R{i+1} : {answers[i]}</div>", unsafe_allow_html=True)
                
    # Affichage de la question courante
    if q_count > 0 and a_count < q_count:
        st.markdown(f"""
        <div class="glass-card">
            <h4>Question du Diagnostic Agent :</h4>
            <p style="font-size: 1.15rem; font-weight: 500; color: #60a5fa;">{questions[-1]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        patient_answer = st.text_input("Votre réponse :", placeholder="Saisissez votre réponse ici...")
        
        if st.button("Envoyer la réponse ✉️", type="primary", use_container_width=True):
            if not patient_answer.strip():
                st.warning("Veuillez saisir une réponse avant d'envoyer.")
            else:
                with st.spinner("Traitement de la réponse par le graphe LangGraph..."):
                    try:
                        res = requests.post(
                            f"{API_URL}/consultation/resume",
                            json={
                                "thread_id": st.session_state.thread_id,
                                "patient_answer": patient_answer
                            }
                        )
                        if res.status_code == 200:
                            data = res.json()
                            st.session_state.state_data = data["state"]
                            st.session_state.current_question = data["current_question"]
                            st.rerun()
                        else:
                            st.error(f"Erreur du backend : {res.text}")
                    except Exception as e:
                        st.error(f"Erreur de connexion : {e}")
                        
    # Bouton de secours si aucune question n'est retournée mais que l'état attend
    else:
        st.warning("En attente d'une action du graphe.")
        if st.button("Forcer la ré-évaluation"):
            st.rerun()

# --- ÉCRAN 3 : Revue Médecin (Human-in-the-Loop) ---
elif status == "waiting_for_physician":
    st.markdown('<div class="step-indicator">Étape 3 : Revue Clinique (Médecin Humain)</div>', unsafe_allow_html=True)
    st.markdown("### 🩺 Interface de validation médicale (Human-in-the-Loop)")
    st.info("Le Diagnostic Agent a terminé l'entretien. Un médecin humain doit maintenant valider le dossier.")
    
    # Affichage complet du dossier
    st.markdown("#### 1. Cas initial décrit par le patient")
    st.write(st.session_state.state_data.get("patient_case"))
    
    st.markdown("#### 2. Entretien clinique (Questions & Réponses)")
    questions = st.session_state.state_data.get("questions", [])
    answers = st.session_state.state_data.get("answers", [])
    for i, (q, a) in enumerate(zip(questions, answers), 1):
        st.markdown(f"**Q{i}** : {q}")
        st.markdown(f"*R* : {a}")
        
    st.markdown("---")
    
    # Section d'évaluation préliminaire
    st.markdown("#### 3. Synthèse clinique préliminaire générée")
    st.markdown(f"""
    <div class="glass-card" style="border-left: 4px solid #8b5cf6;">
        {st.session_state.state_data.get('diagnostic_summary')}
    </div>
    """, unsafe_allow_html=True)
    
    # Signes de gravité (Red Flags)
    red_flags = st.session_state.state_data.get("red_flags", [])
    if red_flags:
        st.markdown(f"""
        <div class="red-flag-alert">
            <strong>⚠️ SIGNE(S) D'ALERTE DÉTECTÉ(S) (RED FLAGS) :</strong>
            <ul>
                {"".join([f"<li>{flag}</li>" for flag in red_flags])}
            </ul>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.success("✅ Aucun signe de gravité clinique évident n'a été automatiquement détecté.")
        
    # Soins intermédiaires recommandés
    st.markdown("#### 4. Recommandation temporaire générée")
    st.info(st.session_state.state_data.get("interim_care"))
    
    # Saisie du médecin
    st.markdown("---")
    st.markdown("#### 5. Avis médical ou Conduite à tenir")
    physician_input = st.text_area(
        "Saisissez vos instructions cliniques, avis ou conduite à tenir (obligatoire pour débloquer le rapport) :",
        placeholder="Exemple : Repos strict pendant 48 heures, surveillance active de la température. Consulter son médecin traitant sous 24h si pas d'amélioration.",
        height=120
    )
    
    if st.button("Valider l'avis médecin et générer le rapport 💾", type="primary", use_container_width=True):
        if not physician_input.strip():
            st.warning("Veuillez saisir un avis médical avant de valider.")
        else:
            with st.spinner("Validation de l'avis et rédaction du rapport final..."):
                try:
                    res = requests.post(
                        f"{API_URL}/consultation/resume",
                        json={
                            "thread_id": st.session_state.thread_id,
                            "physician_treatment": physician_input
                        }
                    )
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state.state_data = data["state"]
                        st.success("Rapport validé et généré !")
                        st.rerun()
                    else:
                        st.error(f"Erreur du backend : {res.text}")
                except Exception as e:
                    st.error(f"Erreur de connexion : {e}")

# --- ÉCRAN 4 : Rapport Final ---
elif status == "completed" or st.session_state.state_data.get("final_report"):
    st.markdown('<div class="step-indicator">Étape 4 : Rapport Clinique Final</div>', unsafe_allow_html=True)
    st.markdown("### 📋 Rapport Final d'Orientation Clinique")
    
    report_content = st.session_state.state_data.get("final_report", "")
    
    st.markdown(f"""
    <div class="glass-card" style="border-top: 4px solid #10b981;">
        {report_content}
    </div>
    """, unsafe_allow_html=True)
    
    # Boutons d'action pour le rapport
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="Télécharger le rapport (Markdown)",
            data=report_content,
            file_name=f"rapport_orientation_{st.session_state.thread_id}.md",
            mime="text/markdown",
            use_container_width=True
        )
    with col2:
        if st.button("Nouvelle consultation 🔄", use_container_width=True):
            reset_consultation()

# Option pour réinitialiser à tout moment
if st.session_state.thread_id:
    st.sidebar.markdown("---")
    st.sidebar.write(f"**Session ID :** `{st.session_state.thread_id}`")
    st.sidebar.write(f"**Statut :** `{status}`")
    if st.sidebar.button("Recommencer à zéro 🔄"):
        reset_consultation()

# Signature
st.markdown('<div class="footer-note">Projet Académique LangGraph Multi-Agents | © 2026</div>', unsafe_allow_html=True)
