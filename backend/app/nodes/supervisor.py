from langgraph.graph import END
from app.state import MedicalState

def supervisor_node(state: MedicalState) -> dict:
    """Nœud superviseur. Il sert de point d'ancrage central pour la prise de décision.
    
    Il n'altère pas l'état lui-même, la logique de routage est déléguée au conditional edge.
    """
    return {}

def route_from_supervisor(state: MedicalState) -> str:
    """Fonction de routage conditionnel qui lit state['next'] pour diriger le workflow.
    
    Si des données requises (réponse patient ou avis médecin) manquent pour passer
    au nœud suivant, elle retourne END afin de suspendre le graphe en attendant l'API.
    """
    next_node = state.get("next", "diagnostic_agent")
    
    if next_node == "diagnostic_agent":
        q_count = state.get("question_count", 0)
        answers = state.get("answers", [])
        
        # Si une question a été posée mais que le patient n'y a pas encore répondu
        if q_count > 0 and len(answers) < q_count:
            return END
            
        return "diagnostic_agent"
        
    elif next_node == "physician_review":
        treatment = state.get("physician_treatment")
        
        # Si le médecin n'a pas encore saisi son avis/traitement, on s'arrête
        if not treatment:
            return END
            
        return "physician_review"
        
    elif next_node == "report_agent":
        return "report_agent"
        
    elif next_node == "FINISH":
        return END
        
    return END
