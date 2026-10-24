from app.state import MedicalState

async def physician_review_node(state: MedicalState) -> dict:
    """Nœud de revue par le médecin (Human-in-the-Loop).
    
    Si 'physician_treatment' est vide, le graphe s'arrête en attente de la saisie.
    Une fois fourni, le graphe passe à l'étape de génération du rapport.
    """
    treatment = state.get("physician_treatment")
    
    if not treatment:
        return {
            "next": "physician_review",
            "status": "waiting_for_physician"
        }
        
    return {
        "next": "report_agent",
        "status": "physician_reviewed"
    }
