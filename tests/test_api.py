from fastapi.testclient import TestClient
from app.api import app

client = TestClient(app)

def test_health():
    """Vérifie le bon fonctionnement de l'endpoint de diagnostic health."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_sessions_start():
    """Vérifie la création d'une nouvelle session de consultation."""
    response = client.post("/sessions/start")
    assert response.status_code == 201
    assert "thread_id" in response.json()

def test_consultation_flow():
    """Vérifie le démarrage et le début de l'enchaînement d'une consultation."""
    # 1. Démarrer la consultation avec un cas patient
    response = client.post("/consultation/start", json={"patient_case": "Toux modérée depuis 3 jours."})
    assert response.status_code == 200
    data = response.json()
    
    assert "thread_id" in data
    assert "current_question" in data
    assert data["status"] == "waiting_for_patient"
    
    thread_id = data["thread_id"]
    
    # 2. Envoyer la première réponse
    response = client.post("/consultation/resume", json={
        "thread_id": thread_id,
        "patient_answer": "Depuis environ 3 jours"
    })
    assert response.status_code == 200
    resume_data = response.json()
    
    assert len(resume_data["state"]["answers"]) == 1
    assert resume_data["state"]["answers"][0] == "Depuis environ 3 jours"
    
    # 3. Consulter les détails du thread
    response = client.get(f"/consultation/{thread_id}")
    assert response.status_code == 200
    state = response.json()
    assert state["patient_case"] == "Toux modérée depuis 3 jours."
    assert len(state["questions"]) >= 1
