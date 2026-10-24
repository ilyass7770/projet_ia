import os
from app.state import MedicalState

def generate_final_report(state: MedicalState) -> str:
    """Génère le rapport d'orientation clinique final.
    
    Utilise OpenAI s'il est disponible, sinon génère un rapport structuré en markdown.
    """
    patient_case = state.get("patient_case", "")
    questions = state.get("questions", [])
    answers = state.get("answers", [])
    summary = state.get("diagnostic_summary", "")
    red_flags = state.get("red_flags", [])
    interim_care = state.get("interim_care", "")
    physician_treatment = state.get("physician_treatment", "")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key.strip() and not api_key.startswith("your_"):
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import SystemMessage, HumanMessage
            
            chat = ChatOpenAI(model="gpt-4o-mini", api_key=api_key, temperature=0.1)
            
            qa_str = "\n".join([f"Q: {q}\nR: {a}" for q, a in zip(questions, answers)])
            red_flags_str = ", ".join(red_flags) if red_flags else "Aucun signe d'alerte détecté."
            
            prompt = (
                f"Rédigez le rapport final d'orientation clinique à partir des éléments suivants :\n"
                f"- Cas initial : {patient_case}\n"
                f"- Entretien (Questions/Réponses) :\n{qa_str}\n"
                f"- Synthèse préliminaire : {summary}\n"
                f"- Signes inquiétants détectés : {red_flags_str}\n"
                f"- Recommandation temporaire : {interim_care}\n"
                f"- Avis et prescription du médecin : {physician_treatment}\n\n"
                "Le rapport doit impérativement respecter la structure markdown suivante :\n"
                "# Rapport final d’orientation clinique\n\n"
                "## 1. Cas Initial du Patient\n"
                "## 2. Questions Posées & Réponses Obtenues\n"
                "## 3. Synthèse Clinique Préliminaire\n"
                "## 4. Signes Inquiétants Détectés\n"
                "## 5. Recommandations de Soins Intermédiaires\n"
                "## 6. Avis ou Conduite à Tenir Proposée par le Médecin\n"
                "## 7. Mention Importante (Clause de non-responsabilité)\n\n"
                "Règle incontournable : la section 7 doit contenir textuellement la phrase :\n"
                "'Ce système ne remplace pas une consultation médicale.'"
            )
            
            messages = [
                SystemMessage(content=(
                    "Vous êtes un assistant IA chargé de rédiger des rapports d'orientation clinique "
                    "précis, formels et prudents. Ne proposez aucun diagnostic définitif."
                )),
                HumanMessage(content=prompt)
            ]
            response = chat.invoke(messages)
            return response.content
        except Exception:
            pass
            
    # Fallback de secours en cas d'absence d'API OpenAI
    red_flags_str = "\n".join([f"- {rf}" for rf in red_flags]) if red_flags else "- Aucun signe d'alerte détecté."
    qa_str = ""
    for i, (q, a) in enumerate(zip(questions, answers), 1):
        qa_str += f"**Q{i}** : {q}\n*Réponse* : {a}\n\n"
        
    report = (
        "# Rapport final d’orientation clinique\n\n"
        "## 1. Cas Initial du Patient\n"
        f"{patient_case}\n\n"
        "## 2. Questions Posées & Réponses Obtenues\n"
        f"{qa_str}"
        "## 3. Synthèse Clinique Préliminaire\n"
        f"{summary}\n\n"
        "## 4. Signes Inquiétants Détectés\n"
        f"{red_flags_str}\n\n"
        "## 5. Recommandations de Soins Intermédiaires\n"
        f"{interim_care}\n\n"
        "## 6. Avis ou Conduite à Tenir Proposée par le Médecin\n"
        f"{physician_treatment}\n\n"
        "## 7. Mention Importante (Clause de non-responsabilité)\n"
        "Ce système ne remplace pas une consultation médicale.\n"
    )
    return report

async def report_agent_node(state: MedicalState) -> dict:
    """Nœud du Report Agent qui génère le rapport final et termine le workflow."""
    report = generate_final_report(state)
    return {
        "final_report": report,
        "next": "FINISH",
        "status": "completed"
    }
