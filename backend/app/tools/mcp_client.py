import os
import logging
from typing import List
from langchain_mcp_adapters.client import MultiServerMCPClient

logger = logging.getLogger(__name__)

def get_local_fallback_guidelines(symptom: str) -> str:
    """Retourne des conseils de secours locaux si le serveur MCP n'est pas accessible."""
    symptom_lower = symptom.lower()
    
    if any(kw in symptom_lower for kw in ["toux", "gorge", "rhume", "nez", "grippe"]):
        guidelines = (
            "Recommandations de secours (Local) :\n"
            "- Reposez-vous et évitez les efforts physiques.\n"
            "- Hydratez-vous régulièrement (eau, tisanes chaudes).\n"
            "- Aérez régulièrement votre logement.\n"
            "- Surveillez votre température corporelle.\n"
            "- Consultez si persistance ou aggravation."
        )
    elif any(kw in symptom_lower for kw in ["fièvre", "fievre", "chaud", "température"]):
        guidelines = (
            "Recommandations de secours (Local) :\n"
            "- Hydratez-vous abondamment pour compenser la perte d'eau.\n"
            "- Reposez-vous dans une pièce fraîche.\n"
            "- Surveillez régulièrement votre température.\n"
            "- Consultez si la fièvre persiste plus de 48h ou dépasse 39°C."
        )
    elif any(kw in symptom_lower for kw in ["respiration", "respirer", "souffle", "thorax", "thoracique", "poitrine", "étouffement"]):
        guidelines = (
            "Recommandations de secours (Local) :\n"
            "- IMPORTANT : Une gêne respiratoire importante ou une douleur thoracique nécessite une évaluation immédiate.\n"
            "- Restez assis ou demi-assis, desserrez les vêtements serrés.\n"
            "- Limitez tout effort physique.\n"
            "- Appelez immédiatement les urgences (le 15 ou le 112) si la gêne s'aggrave rapidement."
        )
    else:
        guidelines = (
            "Recommandations de secours (Local) :\n"
            "- Surveillez attentivement l'évolution de vos symptômes.\n"
            "- Reposez-vous et hydratez-vous correctement.\n"
            "- Consultez un médecin si vos symptômes persistent ou s'aggravent."
        )
        
    guidelines += (
        "\n\n---\n"
        "AVERTISSEMENT :\n"
        "- En cas d'aggravation rapide ou de signe grave, contactez immédiatement les services d'urgence (le 15 ou le 112).\n"
        "- Rappel : Ce conseil de secours ne remplace pas une consultation médicale."
    )
    return guidelines

async def get_guidelines_from_mcp(symptom: str) -> str:
    """Connecte le backend au serveur MCP via MultiServerMCPClient pour récupérer des recommandations."""
    mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:23000/sse")
    
    server_config = {
        "medical_guidelines": {
            "transport": "http",
            "url": mcp_url
        }
    }
    
    try:
        # Tenter d'utiliser MultiServerMCPClient
        async with MultiServerMCPClient(server_config) as client:
            tools = await client.get_tools()
            target_tool = None
            for tool in tools:
                if "get_general_medical_guidelines" in tool.name:
                    target_tool = tool
                    break
                    
            if target_tool:
                res = await target_tool.ainvoke({"symptom": symptom})
                if hasattr(res, "content"):
                    return str(res.content)
                elif isinstance(res, dict) and "content" in res:
                    return str(res["content"])
                return str(res)
            else:
                logger.warning("Outil 'get_general_medical_guidelines' non trouvé sur le serveur MCP.")
                return get_local_fallback_guidelines(symptom)
                
    except Exception as e:
        logger.warning(f"Erreur de connexion au serveur MCP ({e}). Utilisation des recommandations locales.")
        return get_local_fallback_guidelines(symptom)
