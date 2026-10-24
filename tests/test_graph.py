import pytest
from app.state import MedicalState
from app.nodes.supervisor import route_from_supervisor
from app.nodes.diagnostic_agent import diagnostic_agent_node
from app.nodes.physician_review import physician_review_node
from app.nodes.report_agent import report_agent_node
from langgraph.graph import END

@pytest.mark.asyncio
async def test_diagnostic_agent_questions():
    # Test avant d'avoir posé de questions
    state = MedicalState(
        patient_case="Toux depuis hier.",
        questions=[],
        answers=[],
        question_count=0,
        next="diagnostic_agent"
    )
    res = await diagnostic_agent_node(state)
    assert res["question_count"] == 1
    assert len(res["questions"]) == 1
    assert res["next"] == "diagnostic_agent"
    assert res["status"] == "waiting_for_patient"

@pytest.mark.asyncio
async def test_diagnostic_agent_complete():
    # Test après 5 questions-réponses
    state = MedicalState(
        patient_case="Toux légère et fatigue.",
        questions=[
            "Depuis quand avez-vous ces symptômes ?",
            "Avez-vous de la fièvre ? Si oui, quelle température ?",
            "Ressentez-vous une douleur, une gêne respiratoire ou une fatigue importante ?",
            "Avez-vous des antécédents médicaux ou prenez-vous un traitement ?",
            "Les symptômes s’aggravent-ils ou avez-vous remarqué des signes inquiétants ?"
        ],
        answers=["2 jours", "Pas de fièvre", "Fatigue modérée", "Aucun", "Non"],
        question_count=5,
        next="diagnostic_agent"
    )
    res = await diagnostic_agent_node(state)
    assert "diagnostic_summary" in res
    assert "red_flags" in res
    assert "interim_care" in res
    assert res["next"] == "physician_review"
    assert res["status"] == "waiting_for_physician"

@pytest.mark.asyncio
async def test_physician_review_node():
    # Test sans avis médecin
    state = MedicalState(physician_treatment="")
    res = await physician_review_node(state)
    assert res["next"] == "physician_review"
    assert res["status"] == "waiting_for_physician"
    
    # Test avec avis médecin
    state = MedicalState(physician_treatment="Repos préconisé.")
    res = await physician_review_node(state)
    assert res["next"] == "report_agent"
    assert res["status"] == "physician_reviewed"

@pytest.mark.asyncio
async def test_report_agent_node():
    state = MedicalState(
        patient_case="Toux légère.",
        questions=["Q1"],
        answers=["A1"],
        diagnostic_summary="Synthèse clinique préliminaire basée sur les informations fournies. Elle ne constitue pas un diagnostic.",
        red_flags=[],
        interim_care="Repos.",
        physician_treatment="Avis du médecin."
    )
    res = await report_agent_node(state)
    assert "final_report" in res
    assert "Ce système ne remplace pas une consultation médicale." in res["final_report"]
    assert res["next"] == "FINISH"
    assert res["status"] == "completed"

def test_supervisor_routing():
    # Diagnostic en cours, en attente de réponse
    state = MedicalState(next="diagnostic_agent", question_count=1, answers=[])
    assert route_from_supervisor(state) == END
    
    # Diagnostic en cours, réponse fournie
    state = MedicalState(next="diagnostic_agent", question_count=1, answers=["Depuis 2 jours"])
    assert route_from_supervisor(state) == "diagnostic_agent"
    
    # Revue médecin en cours, sans traitement
    state = MedicalState(next="physician_review", physician_treatment="")
    assert route_from_supervisor(state) == END
    
    # Revue médecin en cours, avec traitement
    state = MedicalState(next="physician_review", physician_treatment="Avis du médecin")
    assert route_from_supervisor(state) == "physician_review"
    
    # Report agent
    state = MedicalState(next="report_agent")
    assert route_from_supervisor(state) == "report_agent"
    
    # FINISH
    state = MedicalState(next="FINISH")
    assert route_from_supervisor(state) == END
