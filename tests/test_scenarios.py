import pytest
from fastapi.testclient import TestClient
from app.api import app

client = TestClient(app)

def test_scenario_1_benign_respiratory():
    """Cas 1 : syndrome respiratoire simple
    
    Vérifie : 5 questions posées, synthèse générée, recommandation temporaire générale,
    passage à la revue médecin, et rapport final généré après l'avis du médecin.
    """
    # 1. Démarrer
    response = client.post("/consultation/start", json={
        "patient_case": "Patient avec toux légère, nez qui coule, fatigue modérée depuis 2 jours."
    })
    assert response.status_code == 200
    data = response.json()
    thread_id = data["thread_id"]
    
    # 2. Envoyer les 5 réponses successives
    answers = [
        "Depuis 2 jours précisément.",
        "Pas de fièvre constatée.",
        "Une fatigue légère mais pas de douleur ni gêne respiratoire.",
        "Pas d'antécédents particuliers ni de traitement.",
        "Non, pas d'aggravation rapide."
    ]
    
    for ans in answers:
        response = client.post("/consultation/resume", json={
            "thread_id": thread_id,
            "patient_answer": ans
        })
        assert response.status_code == 200
        data = response.json()
        
    # Après les 5 réponses, le graphe doit être en statut "waiting_for_physician"
    assert data["status"] == "waiting_for_physician"
    state = data["state"]
    assert state["question_count"] == 5
    assert len(state["answers"]) == 5
    assert "diagnostic_summary" in state
    assert "interim_care" in state
    assert "Repos, hydratation" in state["interim_care"]  # Recommandation générale car pas de red flags
    
    # 3. Validation par le médecin
    response = client.post("/consultation/resume", json={
        "thread_id": thread_id,
        "physician_treatment": "Préconisation de repos et de prise de tisanes chaudes. Surveiller pendant 48 heures."
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    
    # Vérifier la présence du rapport final et de la clause de non-responsabilité
    report = data["state"]["final_report"]
    assert "Rapport final d’orientation clinique" in report
    assert "Ce système ne remplace pas une consultation médicale." in report

def test_scenario_2_red_flags():
    """Cas 2 : cas avec red flags
    
    Vérifie : red_flags non vide, recommandation prudente d'orientation vers les urgences,
    pas de diagnostic définitif, intervention médecin obligatoire.
    """
    # 1. Démarrer
    response = client.post("/consultation/start", json={
        "patient_case": "Patient avec douleur thoracique, difficulté respiratoire et fièvre élevée."
    })
    assert response.status_code == 200
    data = response.json()
    thread_id = data["thread_id"]
    
    # 2. Envoyer les 5 réponses successives
    answers = [
        "Depuis ce matin à 6h.",
        "Oui, j'ai une fièvre élevée mesurée à 39.5°C.",
        "Oui, grosse douleur dans la poitrine et j'ai beaucoup de mal à respirer en restant assis.",
        "Je prends un traitement pour l'hypertension.",
        "Oui, la douleur est de plus en plus forte et s'aggrave rapidement."
    ]
    
    for ans in answers:
        response = client.post("/consultation/resume", json={
            "thread_id": thread_id,
            "patient_answer": ans
        })
        assert response.status_code == 200
        data = response.json()
        
    # Le graphe doit être arrêté en attente du médecin
    assert data["status"] == "waiting_for_physician"
    state = data["state"]
    
    # Vérifier la détection des red flags et la recommandation d'urgences
    assert len(state["red_flags"]) > 0
    assert "difficulté respiratoire" in state["red_flags"] or "douleur thoracique" in state["red_flags"]
    assert "Présence de signes nécessitant une attention rapide" in state["interim_care"]
    
    # Vérifier l'absence de diagnostic définitif
    assert "diagnostic_summary" in state
    assert "Synthèse clinique préliminaire basée sur les informations fournies. Elle ne constitue pas un diagnostic." in state["diagnostic_summary"]

def test_scenario_3_benign_effort():
    """Cas 3 : cas bénin
    
    Vérifie : pas de red flags détectés, recommandation générale, rapport final généré après avis.
    """
    # 1. Démarrer
    response = client.post("/consultation/start", json={
        "patient_case": "Patient avec fatigue légère après effort physique intense, sans fièvre ni douleur."
    })
    assert response.status_code == 200
    data = response.json()
    thread_id = data["thread_id"]
    
    # 2. Envoyer les 5 réponses successives
    answers = [
        "Depuis la fin de ma course hier après-midi.",
        "Non, pas de fièvre.",
        "Seulement de la fatigue, aucune gêne respiratoire.",
        "Aucun antécédent médical.",
        "Non, la fatigue s'estompe progressivement."
    ]
    
    for ans in answers:
        response = client.post("/consultation/resume", json={
            "thread_id": thread_id,
            "patient_answer": ans
        })
        assert response.status_code == 200
        data = response.json()
        
    assert data["status"] == "waiting_for_physician"
    state = data["state"]
    
    # Aucun red flag ne doit être présent
    assert len(state["red_flags"]) == 0
    assert "Repos, hydratation" in state["interim_care"]
    
    # 3. Avis médecin
    response = client.post("/consultation/resume", json={
        "thread_id": thread_id,
        "physician_treatment": "Bonne hydratation et reprise douce du sport après 24h de repos."
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
