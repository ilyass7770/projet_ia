import logging
from mcp.server.fastmcp import FastMCP

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_medical_guidelines")

# Initialisation de FastMCP sur le port 23000
mcp = FastMCP("Medical Guidelines Server", port=23000)

@mcp.tool()
def get_general_medical_guidelines(symptom: str) -> str:
    """Retourne des recommandations générales non diagnostiques pour un symptôme donné.
    
    Args:
        symptom (str): Le symptôme décrit par le patient.
    """
    logger.info(f"Recherche de recommandations pour le symptôme : {symptom}")
    
    symptom_lower = symptom.lower()
    
    # Recommandations personnalisées selon le type de symptômes rencontrés
    if any(kw in symptom_lower for kw in ["toux", "gorge", "rhume", "nez", "grippe"]):
        guidelines = (
            "Recommandations générales pour les symptômes respiratoires légers :\n"
            "- Reposez-vous et évitez les efforts physiques intenses.\n"
            "- Hydratez-vous régulièrement (eau, tisanes chaudes).\n"
            "- Aérez régulièrement votre logement.\n"
            "- Surveillez votre température corporelle.\n"
            "- Consultez un médecin si les symptômes persistent au-delà de quelques jours ou s'aggravent."
        )
    elif any(kw in symptom_lower for kw in ["fièvre", "fievre", "chaud", "température"]):
        guidelines = (
            "Recommandations générales en cas de fièvre :\n"
            "- Hydratez-vous abondamment pour compenser la perte d'eau.\n"
            "- Reposez-vous dans une pièce fraîche et aérée.\n"
            "- Ne surchauffez pas votre logement et portez des vêtements légers.\n"
            "- Surveillez régulièrement votre température (matin et soir).\n"
            "- En cas de fièvre très élevée (> 39°C) ou persistante plus de 48h, consultez un médecin."
        )
    elif any(kw in symptom_lower for kw in ["respiration", "respirer", "souffle", "thorax", "thoracique", "poitrine", "étouffement"]):
        guidelines = (
            "Recommandations et vigilance en cas de gêne respiratoire ou thoracique :\n"
            "- IMPORTANT : Une gêne respiratoire importante ou une douleur thoracique nécessite une évaluation immédiate.\n"
            "- Restez assis ou demi-assis, desserrez les vêtements serrés.\n"
            "- Limitez tout effort physique.\n"
            "- Appelez immédiatement les urgences (le 15 ou le 112) si la gêne s'aggrave rapidement ou s'accompagne d'une douleur oppressive dans la poitrine."
        )
    elif any(kw in symptom_lower for kw in ["fatigue", "fatigué", "faiblesse"]):
        guidelines = (
            "Recommandations générales en cas de fatigue :\n"
            "- Accordez-vous des plages de repos et veillez à avoir un sommeil de qualité.\n"
            "- Alimentez-vous de manière équilibrée et hydratez-vous.\n"
            "- Si la fatigue s'accompagne de fièvre, de douleurs ou persiste anormalement, prenez rendez-vous chez votre médecin."
        )
    else:
        guidelines = (
            f"Recommandations générales pour les symptômes évoqués ('{symptom}') :\n"
            "- Surveillez attentivement l'évolution de votre état général.\n"
            "- Reposez-vous et hydratez-vous correctement.\n"
            "- Évitez l'automédication sans l'avis préalable d'un professionnel.\n"
            "- Consultez un médecin si vos symptômes s'aggravent ou ne s'améliorent pas rapidement."
        )
        
    # Mention obligatoire et rappel des urgences
    guidelines += (
        "\n\n---\n"
        "AVERTISSEMENT :\n"
        "- En cas d'aggravation rapide ou de signe grave (difficulté à respirer, douleur thoracique intense, perte de connaissance, confusion, saignement important), contactez immédiatement les services d'urgence (le 15 ou le 112).\n"
        "- Rappel : Ce système ne remplace pas une consultation médicale."
    )
    
    return guidelines

if __name__ == "__main__":
    mcp.run(transport="sse")
