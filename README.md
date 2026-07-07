# 🫀 CardioCare — Digitale EKG-Datenbank

**Eine rollenbasierte Streamlit-Anwendung zur Verwaltung, Analyse und Visualisierung von EKG-Daten**
*Entwickelt von Melanie Pfusterer, Lisa Raffler & Vanessa Reich*

---

## Inhaltsverzeichnis

- [Über das Projekt](#über-das-projekt)
- [Funktionen](#funktionen)
- [Screenshots](#screenshots)
- [Tech-Stack](#tech-stack)
- [Projektstruktur](#projektstruktur)
- [Installation](#installation)
- [Nutzung](#nutzung)
- [Datenmodell](#datenmodell)
- [Sicherheit](#sicherheit)
- [Bekannte Einschränkungen & Ausblick](#bekannte-einschränkungen--ausblick)

---

## Über das Projekt

**CardioCare** ist eine digitale EKG-Datenbank für medizinisches Personal und Patient*innen. Die Anwendung
ermöglicht die zentrale Verwaltung von Patientenprofilen, den Upload und die Auswertung von EKG-Aufzeichnungen
(als `.txt`-Rohdaten oder `.fit`-Aktivitätsdateien) sowie den visuellen Vergleich mehrerer Tests inklusive
automatischer Peak- und HRV-Berechnung.

Die App unterscheidet strikt zwischen drei Rollen — **Admin**, **Doctor** und **Patient** — und zeigt
abhängig von der Rolle jeweils nur die passenden Funktionen und Daten an.

## Funktionen

| 🔐 **Login & Rollen** | Anmeldung für `admin`, `doctor` und `patient` mit SHA-256-gehashten Passwörtern und automatischer Migration alter Klartext-Passwörter |
| 🧑‍🤝‍🧑 **Patientenverwaltung** | Anlegen, Suchen, Bearbeiten und Löschen von Patient*innenprofilen inkl. Profilbild |
| 📤 **EKG-Upload** | Hinzufügen neuer Tests im Format `.txt` (Rohsignal) oder `.fit` (Aktivitätsdaten mit synthetisiertem EKG) |
| 📊 **Analyse** | Automatische Peak-Erkennung, Herzfrequenz- und HRV(RMSSD)-Berechnung sowie interaktive Zeitreihen-Plots |
| ↔️ **Vergleichsansicht** | Überlagerung zweier Tests — desselben oder zweier verschiedener Patient*innen — mit Zeitfenster-Slider und Kennzahlenvergleich |
| 📝 **Notizen** | Persönliche Notizen anlegen und löschen |
| 🔑 **Automatische Zugänge** | Für neu angelegte Patient*innen wird automatisch ein Zugang samt Passwort generiert |

## Screenshots

<img src="data/images/Auswahl_Patienten.png" alt="Patientenauswahl" width="45%">
<img src="data/images/PatientenSeite.png" alt="Patientenansicht" width="45%">

## Tech-Stack

- **Frontend/Framework:** [Streamlit](https://streamlit.io/)
- **Datenverarbeitung:** pandas, NumPy, SciPy
- **Visualisierung:** Plotly
- **Datenhaltung:** TinyDB (`persons.db.json`), JSON-Dateien (`users.json`, `notes.json`)
- **FIT-Datenparsing:** fitparse
- **Sicherheit:** hashlib (SHA-256)

Die vollständige Liste aller Abhängigkeiten befindet sich in [`requirements.txt`](requirements.txt).

## Projektstruktur

Abgabe_4/
├── main.py                        # Einstiegspunkt der Streamlit-App
├── requirements.txt
├── backend/
│   ├── module_klassen/
│   │   ├── person.py               # Klasse Person (Profil, EKG-Tests, TinyDB-Anbindung)
│   │   ├── ekgdata.py              # Klasse EKGdata: Laden, Peaks, HR/HRV, Plots (.txt)
│   │   └── fitdata.py              # Klasse FITdata: Laden & Aufbereitung von .fit-Dateien
│   ├── funktionen/
│   │   ├── loader.py
│   │   └── notes.py
│   └── utils/
│       ├── peak_detection.py       # Peak-Erkennung im Rohsignal
│       ├── hrv.py                  # HRV-RMSSD-Berechnung
│       ├── filter_persons.py
│       └── seitenfunktionen.py
├── frontend/
│   ├── app_steuerung/
│   │   ├── steuerung.py            # Haupt-UI-Controller (Klasse App) — Seiten & Router
│   │   ├── navigation.py           # Seitennavigation
│   │   ├── person_manager.py       # Laden/Filtern/Löschen von Personen
│   │   └── session.py              # Session-State-Initialisierung
│   ├── ekg_plot/
│   │   ├── analysis_manager.py     # Steuert die Auswertungs-Tabs
│   │   ├── compare.py              # Overlay-Plots & Kennzahlenvergleich
│   │   └── utlispatient.py         # Hilfsfunktionen für Vergleichspatienten
│   ├── Login/
│   │   └── login.py                # LoginManager: Login/Logout, Passwort-Hashing
│   └── Notizen/
│       └── notizen.py              # Laden/Speichern/Löschen von Notizen
├── funktionen/
│   └── hrv.py
└── data/
    ├── users.json                  # Benutzerkonten (Rollen, gehashte Passwörter)
    ├── persons.db.json             # TinyDB-Datenbank mit Patient*innen & EKG-Tests
    ├── notes.json                  # Notizen je Benutzer
    ├── ekg_data/                   # Rohdaten (.txt / .fit) der EKG-Tests
    └── images/                     # Profilbilder, Logo, Screenshots

## Installation

**Voraussetzung:** Python 3.11+

1. Repository klonen und in das Projektverzeichnis wechseln
   git clone https://github.com/vanessaare/Abgabe_4.git
   cd Abgabe_4

2. Abhängigkeiten installieren (idealerweise in einer virtuellen Umgebung)
   pip install -r requirements.txt

3. Anwendung starten
   streamlit run main.py

## Nutzung

### Rolle `admin` / `doctor`
- Patient*innen anlegen, suchen, bearbeiten und löschen
- Neue EKG-Tests hochladen (`.txt` oder `.fit`)
- EKG-Signale analysieren (Peaks, Herzfrequenz, HRV)
- Zwei Tests vergleichen — desselben Patienten oder zweier verschiedener Patient*innen

### Rolle `patient`
- Eigene EKG-Daten und Analysen einsehen (nur lesend)
- Zwei eigene Tests miteinander vergleichen
- Persönliche Notizen anlegen und löschen
- Direkter Logout über die Startseite

### Passwort-Logik für automatisch angelegte Patientenkonten
Format: erste 3 Buchstaben Vorname + erste 3 Buchstaben Nachname + letzte 2 Ziffern Geburtsjahr
(z. B. *Anne Mayer, geb. 2001* → `annmay01`). Das generierte Passwort wird beim Anlegen einmalig im
Klartext angezeigt und danach ausschließlich gehasht gespeichert.

## Datenmodell

| Datei | Inhalt |
| `data/users.json` | Benutzername → `{password (SHA-256), role, person_id?}` |
| `data/persons.db.json` | TinyDB-Tabelle mit `id`, `firstname`, `lastname`, `date_of_birth`, `gender`, `picture_path`, `ekg_tests[]` |
| `data/notes.json` | Notizen je Benutzer, z. B. `{"doctor1": [{"datum": "03.07.2026", "text": "..."}]}` |
| `data/ekg_data/*.txt` | Tab-getrennte Rohsignale (`Messwerte in mV`, `Zeit in ms`) |
| `data/ekg_data/*.fit` | Garmin-/ANT-FIT-Aktivitätsdateien mit Herzfrequenzverlauf |

## Sicherheit

- Passwörter werden mit `hashlib.sha256` gehasht in `data/users.json` gespeichert.
- Bestehende Klartext-Passwörter werden beim ersten erfolgreichen Login automatisch migriert.
- Zugriff auf Bearbeitungs- und Upload-Funktionen ist auf die Rollen `admin` und `doctor` beschränkt.