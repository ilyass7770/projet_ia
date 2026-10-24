from typing import TypedDict, Annotated, Literal, List
from langgraph.graph.message import add_messages

class MedicalState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    next: Literal["diagnostic_agent", "physician_review", "report_agent", "FINISH"]
    patient_case: str
    questions: List[str]
    answers: List[str]
    question_count: int
    diagnostic_summary: str
    interim_care: str
    physician_treatment: str
    final_report: str
    status: str
    red_flags: List[str]
    thread_id: str
