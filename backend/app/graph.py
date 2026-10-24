from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.state import MedicalState
from app.nodes.supervisor import supervisor_node, route_from_supervisor
from app.nodes.diagnostic_agent import diagnostic_agent_node
from app.nodes.physician_review import physician_review_node
from app.nodes.report_agent import report_agent_node

# Construction du graphe
builder = StateGraph(MedicalState)

# Ajout des nœuds
builder.add_node("supervisor", supervisor_node)
builder.add_node("diagnostic_agent", diagnostic_agent_node)
builder.add_node("physician_review", physician_review_node)
builder.add_node("report_agent", report_agent_node)

# Configuration de l'entrée vers le superviseur
builder.add_edge(START, "supervisor")

# Routage conditionnel depuis le superviseur
builder.add_conditional_edges(
    "supervisor",
    route_from_supervisor,
    {
        "diagnostic_agent": "diagnostic_agent",
        "physician_review": "physician_review",
        "report_agent": "report_agent",
        END: END
    }
)

# Retours au superviseur après l'exécution d'un nœud agent
builder.add_edge("diagnostic_agent", "supervisor")
builder.add_edge("physician_review", "supervisor")
builder.add_edge("report_agent", "supervisor")

# Utilisation d'un checkpointer en mémoire pour sauvegarder l'état entre les appels d'API (Human-in-the-Loop)
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)
