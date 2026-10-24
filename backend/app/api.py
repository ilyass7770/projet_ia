import uuid
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Chargement des variables d'environnement (.env)
load_dotenv()

from app.graph import graph
from app.storage import memory_store

# Configurer les logs pour suivre le graphe et les requêtes
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api_medical_system")

app = FastAPI(
    title="Système Multi-Agents Médical avec LangGraph",
    description="API d'orientation clinique préliminaire académique",
    version="1.0.0"
)

# Configuration CORS pour autoriser le frontend Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles de données Pydantic
class StartConsultationRequest(BaseModel):
    patient_case: str

class ResumeConsultationRequest(BaseModel):
    thread_id: str
    patient_answer: Optional[str] = None
    physician_treatment: Optional[str] = None

@app.post("/sessions/start", status_code=status.HTTP_201_CREATED)
async def start_session():
    """Crée une nouvelle session de consultation et retourne un thread_id."""
    thread_id = str(uuid.uuid4())
    initial_state = {
        "thread_id": thread_id,
        "status": "created",
        "questions": [],
        "answers": [],
        "question_count": 0
    }
    memory_store.create_session(thread_id, initial_state)
    logger.info(f"Session initialisée avec le thread_id : {thread_id}")
    return {"thread_id": thread_id}

@app.post("/consultation/start", status_code=status.HTTP_200_OK)
async def start_consultation(body: StartConsultationRequest):
    """Initialise l'état avec le cas patient et lance le workflow du graphe LangGraph."""
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    initial_state = {
        "patient_case": body.patient_case,
        "questions": [],
        "answers": [],
        "question_count": 0,
        "next": "diagnostic_agent",
        "status": "started",
        "thread_id": thread_id
    }
    
    try:
        # Invocation asynchrone du graphe avec l'état initial
        result_state = await graph.ainvoke(initial_state, config)
        
        # Enregistrement dans le stockage local
        memory_store.create_session(thread_id, result_state)
        
        current_question = None
        if result_state.get("questions"):
            current_question = result_state["questions"][-1]
            
        return {
            "thread_id": thread_id,
            "state": result_state,
            "current_question": current_question,
            "status": result_state.get("status", "started")
        }
    except Exception as e:
        logger.error(f"Erreur lors du démarrage du graphe pour la session {thread_id} : {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du démarrage de la consultation : {str(e)}"
        )

@app.post("/consultation/resume", status_code=status.HTTP_200_OK)
async def resume_consultation(body: ResumeConsultationRequest):
    """Reprend le workflow en y ajoutant la réponse du patient ou l'avis du médecin."""
    thread_id = body.thread_id
    config = {"configurable": {"thread_id": thread_id}}
    
    # 1. Récupération de la session
    state_snapshot = await graph.aget_state(config)
    if not state_snapshot or not state_snapshot.values:
        local_session = memory_store.get_session(thread_id)
        if not local_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session non trouvée"
            )
        current_values = local_session
    else:
        current_values = dict(state_snapshot.values)
        
    # 2. Mise à jour de l'état (checkpointer) selon l'entrée reçue
    updates = {}
    if body.patient_answer is not None:
        answers = list(current_values.get("answers", []))
        answers.append(body.patient_answer)
        updates["answers"] = answers
        updates["next"] = "diagnostic_agent"
        
    if body.physician_treatment is not None:
        updates["physician_treatment"] = body.physician_treatment
        updates["next"] = "report_agent"
        
    if updates:
        await graph.aupdate_state(config, updates)
        
    try:
        # 3. Invocation du graphe pour avancer au prochain point d'arrêt
        result_state = await graph.ainvoke(None, config)
        
        # Mise à jour du stockage local
        memory_store.update_session(thread_id, result_state)
        
        current_question = None
        # Si une nouvelle question a été posée, on la récupère pour le frontend
        q_len = len(result_state.get("questions", []))
        a_len = len(result_state.get("answers", []))
        if q_len > 0 and a_len < q_len:
            current_question = result_state["questions"][-1]
            
        return {
            "thread_id": thread_id,
            "state": result_state,
            "current_question": current_question,
            "status": result_state.get("status", "running")
        }
    except Exception as e:
        logger.error(f"Erreur lors de la reprise du graphe pour la session {thread_id} : {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la reprise de la consultation : {str(e)}"
        )

@app.get("/consultation/{thread_id}", status_code=status.HTTP_200_OK)
async def get_consultation(thread_id: str):
    """Retourne l'état complet actuel de la consultation."""
    config = {"configurable": {"thread_id": thread_id}}
    state_snapshot = await graph.aget_state(config)
    
    if not state_snapshot or not state_snapshot.values:
        local_session = memory_store.get_session(thread_id)
        if not local_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consultation non trouvée"
            )
        return local_session
        
    return dict(state_snapshot.values)

@app.get("/consultation/{thread_id}/report", status_code=status.HTTP_200_OK)
async def get_consultation_report(thread_id: str):
    """Retourne uniquement le rapport final si celui-ci a été généré."""
    config = {"configurable": {"thread_id": thread_id}}
    state_snapshot = await graph.aget_state(config)
    
    if not state_snapshot or not state_snapshot.values:
        local_session = memory_store.get_session(thread_id)
        if not local_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consultation non trouvée"
            )
        report = local_session.get("final_report")
    else:
        report = state_snapshot.values.get("final_report")
        
    if not report:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le rapport final d'orientation n'est pas encore disponible. Veuillez valider toutes les étapes."
        )
        
    return {"final_report": report}

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Permet de vérifier le bon fonctionnement de l'API."""
    return {"status": "ok"}
