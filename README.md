# Abschlussprojekt

**Teilnehmerinnen:** Melanie Pfusterer, Lisa Raffler, Vanessa Reich

Digitales EKG-Verwaltungssystem mit Streamlit. Die Anwendung ist als Patientenverwaltung für medizinisches Personal und Patient*innen konzipiert.

## Was das Projekt kann

- Rollenbasierte Anmeldung für `admin`, `doctor` und `patient`
- Zentrale Verwaltung von Patient*innenprofilen
- Anzeige von EKG-Daten, Analyseergebnissen und Vergleichsansichten
- Upload neuer EKG-Tests und Speicherung in der Datenbank
- Sichere Passwortspeicherung mit SHA-256 Hashing
- Automatische Generierung neuer Patientenpasswörter



## Installationsanleitung

1. Abhängigkeiten installieren
   ```bash
   pip install -r requirements.txt
   ```

2. Anwendung starten
   ```bash
   streamlit run main.py
   ```

## Projektübersicht

### `main.py`
Startet die Streamlit-Anwendung.

### `backend/`
- Verarbeitet Patienten- und EKG-Daten
- Enthält Klassen zur Datenbankanbindung und Datenaufbereitung

### `backend/funktionen/notizen.py`
- Stellt die Notiz-API bereit: `lade_notizen`, `speichere_notizen`, `notiz_hinzufuegen`, `notiz_loeschen`.

### `frontend/`
- Stellt die Benutzeroberfläche und Navigation bereit
- Verwaltet Login, Logout, Rollen und Seitensteuerung

Wichtige Dateien:
- `frontend/app/steuerung.py`: Haupt-UI-Controller (class `App`) — hier sind Seiten wie `home`, `select`, `analysis`, `notes` implementiert.
- `frontend/login.py`: Login/Logout, Passwort-Hashing und Migration von Klartext-Passwörtern.
- `frontend/app/components/notizen.py`: UI-Wrapper für Notizen (Laden, Speichern, Löschen).

### `funktionen/`
- Enthält Hilfsfunktionen für Filter, HRV-Berechnung und Peak-Detektion

### `data/`
- `users.json`: Benutzerkonten mit Rollen und gehashten Passwörtern
- `persons.db.json`: Patientenprofile und zugehörige EKG-Tests
- `ekg_data/`: Rohdaten für EKG-Tests
- `images/`: Bilder, die im Frontend angezeigt werden
- `notes.json`: Persönliche Notizen, organisiert nach Benutzern (z. B. `{ "doctor1": [ {"datum": "03.07.2026", "text": "..."} ] }`).

## Wichtige Details

- Patient*innen-Passwörter werden automatisch generiert und nur als Hash gespeichert.
- Das Format für generierte Passwörter ist:
  - erste 3 Buchstaben Vorname + erste 3 Buchstaben Nachname + letzte 2 Ziffern Geburtsjahr
- Bestehende Klartext-Passwörter werden beim ersten Login automatisch auf Hash umgestellt.

Weitere Hinweise zur Sicherheit:
- Passwörter werden mit `hashlib.sha256` gehasht und in `data/users.json` gespeichert. Alte Klartext-Passwörter werden bei erfolgreichem Login migriert.

## Nutzung

- `admin` / `doctor`
  - können Patient*innen anlegen und löschen
  - können Patient*innen suchen und analysieren
  - können EKG-Testdaten vergleichen

- `patient`
  - kann eigene EKG-Daten anzeigen
  - kann eigene Analyse-Seite aufrufen
  - hat direkten Logout-Button auf der Startseite
  - kann persönliche Notizen ansehen, hinzufügen und löschen

## Erweiterungsmöglichkeiten

- Passwort-Reset für Patient*innen
- Zusätzliche EKG-Formate und Importfunktionen
- Erweiterte Vergleichsvisualisierungen
- Verbesserte mobile Darstellung

## Debug & Entwicklung

- Logs und Fehler erscheinen in der Konsole, wenn `streamlit run main.py` verwendet wird.
- Wenn UI-Aktionen (z. B. Löschen einer Notiz) unerwartetes Verhalten zeigen, prüfe `data/notes.json` und die Konsole-Ausgabe.

---

Falls du möchtest, übernehme ich noch eine kurze Release-Note oder ein Changelog-File mit den letzten Änderungen.
