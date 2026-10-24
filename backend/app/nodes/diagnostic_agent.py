import os
from app.state import MedicalState
from app.tools.patient_tools import get_next_question, detect_red_flags
from app.tools.care_tools import recommend_interim_care

def generate_summary(patient_case: str, questions: list, answers: list) -> str:
    """Génère la synthèse clinique préliminaire.
    
    Tente d'utiliser ChatOpenAI s'il est configuré, sinon utilise une mise en forme de secours.
    La synthèse doit impérativement inclure la clause de prudence.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key.strip() and not api_key.startswith("your_"):
        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import SystemMessage, HumanMessage
            
            chat = ChatOpenAI(model="gpt-4o-mini", api_key=api_key, temperature=0.2)
            
            qa_str = "\n".join([f"Q: {q}\nR: {a}" for q, a in zip(questions, answers)])
            prompt = (
                f"Description initiale du patient : {patient_case}\n\n"
                f"Questions posées et réponses :\n{qa_str}\n\n"
                "Rédigez une synthèse clinique préliminaire structurée et prudente. "
                "Ne donnez pas de diagnostic définitif. Précisez bien que ceci est une orientation."
            )
            
            messages = [
                SystemMessage(content=(
                    "Vous êtes un assistant IA d'orientation clinique préliminaire. Votre synthèse doit être prudente, "
                    "factuelle, structurée, et commencer par la phrase exacte : "
                    "'Synthèse clinique préliminaire basée sur les informations fournies. Elle ne constitue pas un diagnostic.'"
                )),
                HumanMessage(content=prompt)
            ]
            response = chat.invoke(messages)
            return response.content
        except Exception as e:
            # En cas d'erreur de clé ou de réseau, on bascule sur la version locale
            pass
            
    # Version locale déterministe
    summary = (
        "Synthèse clinique préliminaire basée sur les informations fournies. "
        "Elle ne constitue pas un diagnostic.\n\n"
        f"**Cas initial décrit par le patient :**\n{patient_case}\n\n"
        "**Détails cliniques recueillis lors de l'entretien :**\n"
    )
    for i, (q, a) in enumerate(zip(questions, answers), 1):
        summary += f"- **Question {i}** : {q}\n  *Réponse* : {a}\n"
    return summary

async def diagnostic_agent_node(state: MedicalState) -> dict:
    """Nœud de l'agent de diagnostic.
    
    Il pose 5 questions successivement, puis compile la synthèse clinique préliminaire,
    détecte les red flags et propose des recommandations intermédiaires.
    """
    patient_case = state.get("patient_case", "")
    questions = list(state.get("questions", []))
    answers = list(state.get("answers", []))
    question_count = state.get("question_count", 0)
    
    # Si le patient n'a pas répondu à la dernière question posée, on attend
    if question_count > 0 and len(answers) < question_count:
        return {
            "next": "diagnostic_agent",
            "status": "waiting_for_patient"
        }
        
    # Si on a posé moins de 5 questions, on génère la suivante
    if question_count < 5:
        next_q = get_next_question(question_count, patient_case, answers)
        if next_q:
            questions.append(next_q)
            return {
                "questions": questions,
                "question_count": len(questions),
                "next": "diagnostic_agent",
                "status": "waiting_for_patient"
            }
            
    # Si on a posé les 5 questions et qu'on a reçu les 5 réponses
    if question_count == 5 and len(answers) == 5:
        # Détection des red flags
        red_flags = detect_red_flags(patient_case, answers)
        
        # Recommandations intermédiaires
        interim_care = recommend_interim_care(patient_case, answers, red_flags)
        
        # Synthèse clinique préliminaire
        summary = generate_summary(patient_case, questions, answers)
        
        return {
            "diagnostic_summary": summary,
            "red_flags": red_flags,
            "interim_care": interim_care,
            "next": "physician_review",
            "status": "waiting_for_physician"
        }
        
    return {}
