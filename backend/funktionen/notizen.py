from datetime import datetime
import json
import os
from typing import List, Dict

DATEI = "data/notes.json"


def _ensure_file():
    """Erstellt die Notizdatei, falls sie noch nicht existiert."""
    if not os.path.exists(os.path.dirname(DATEI)):
        os.makedirs(os.path.dirname(DATEI), exist_ok=True)
    if not os.path.exists(DATEI):
        with open(DATEI, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)


def lade_notizen() -> Dict[str, List[Dict]]:
    """Lädt alle Notizen (nach Benutzer) aus der JSON-Datei."""
    _ensure_file()
    with open(DATEI, "r", encoding="utf-8") as f:
        return json.load(f)


def speichere_notizen(notizen: Dict[str, List[Dict]]):
    """Speichert das komplette Notizen-Dictionary in die Datei."""
    _ensure_file()
    with open(DATEI, "w", encoding="utf-8") as f:
        json.dump(notizen, f, ensure_ascii=False, indent=2)


def notiz_hinzufuegen(username: str, text: str):
    """Fügt für `username` eine neue Notiz mit aktuellem Datum hinzu."""
    if not text:
        return
    notizen = lade_notizen()
    if username not in notizen:
        notizen[username] = []
    neue_notiz = {"datum": datetime.now().strftime("%d.%m.%Y"), "text": text}
    notizen[username].append(neue_notiz)
    speichere_notizen(notizen)


def hole_notizen(username: str) -> List[Dict]:
    """Gibt die Liste der Notizen für `username` zurück."""
    notizen = lade_notizen()
    return notizen.get(username, [])


def notiz_loeschen(username: str, index: int) -> bool:
    """Löscht die Notiz an Position `index` für `username`.

    Gibt True zurück, wenn erfolgreich, False wenn Index ungültig.
    """
    notizen = lade_notizen()
    user_notes = notizen.get(username)
    if not user_notes:
        return False
    if index < 0 or index >= len(user_notes):
        return False
    # Entfernen und speichern
    user_notes.pop(index)
    notizen[username] = user_notes
    speichere_notizen(notizen)
    return True