import streamlit as st
from backend.other_modules.notes import hole_notizen, notiz_hinzufuegen, notiz_loeschen
from typing import List, Dict


def load_notes() -> List[Dict]:
    """Lädt die Notizen des aktuellen Benutzers (als Liste von Dicts)."""
    username = st.session_state.get("username") or "guest"
    return hole_notizen(username)


def save_note(text: str):
    """Speichert eine neue Notiz für den aktuellen Benutzer."""
    username = st.session_state.get("username") or "guest"
    notiz_hinzufuegen(username, text)


def delete_note(index: int) -> bool:
    """Löscht die Notiz mit dem gegebenen Index für den aktuellen Benutzer.

    Gibt True zurück, wenn die Notiz gelöscht wurde.
    """
    username = st.session_state.get("username") or "guest"
    return notiz_loeschen(username, index)


