from typing import Dict, Any, Optional

# Dictionnaire global pour stocker les sessions en mémoire
_SESSIONS: Dict[str, Dict[str, Any]] = {}

def create_session(thread_id: str, state: Dict[str, Any]) -> None:
    """Crée une nouvelle session avec un état initial."""
    _SESSIONS[thread_id] = dict(state)

def get_session(thread_id: str) -> Optional[Dict[str, Any]]:
    """Récupère l'état d'une session par son thread_id."""
    session = _SESSIONS.get(thread_id)
    if session is not None:
        return dict(session)
    return None

def update_session(thread_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Met à jour l'état d'une session existante."""
    if thread_id in _SESSIONS:
        _SESSIONS[thread_id].update(updates)
        return dict(_SESSIONS[thread_id])
    return None

def delete_session(thread_id: str) -> bool:
    """Supprime une session."""
    if thread_id in _SESSIONS:
        del _SESSIONS[thread_id]
        return True
    return False

def list_sessions() -> Dict[str, Dict[str, Any]]:
    """Retourne la liste de toutes les sessions actives."""
    return dict(_SESSIONS)
