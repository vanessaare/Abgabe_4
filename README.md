# Abgabe_4

**Teilnehmerinnen:** Melanie Pfusterer, Lisa Raffler, Vanessa Reich

Das Projekt erstellt eine mithilfe von Streamlit eine **Webseite**, die als eine Art Datenbank dienen soll. 
In der man, verschiedene Probanden auswählen kann, diese dann angezeigen kann und weitere Attribute die zu diesen gehören ebenso zeigen. 
Desweiteren wir ein **EKG Diagramm** erstellt bei den Probanden auf ihrer eigenen Datenseite. 

Zur Installation des Projekts wird pip verwendet.

## Um die Webseite anzeigen zu lassen, muss folgendermaßen vorgegangen werden:

1. Installation der Abhängigkeiten
   **->** pip install -r requirements.txt

2. Projekt starten
   **->** streamlit run main.py

## Was macht das Projekt?

- Lädt EKG‑Rohdaten und Stammdaten aus dem data/‑Ordner.

- Bereitet die EKG‑Signale auf und erkennt Peaks (R‑Zacken).

- Visualisiert die EKG‑Kurven im Frontend (Streamlit‑Weboberfläche).

- Zeigt Patient*inneninformationen und zugehörige Bilder an.

- Ermöglicht die Auswahl verschiedener Datensätze über eine interaktive Oberfläche.


## Projektstruktur

* **main.py**
  Zentrales Startskript des Projekts. 
  Hier wird der Gesamtworkflow initialisiert und die Verbindung zwischen Frontend, Backend und Funktionsmodulen hergestellt.

* **backend/**
 Zentrales Startskript des Projekts.
 Hier wird der Gesamtworkflow initialisiert und die Verbindung zwischen Frontend, Backend und Funktionsmodulen hergestellt.

* **frontend/**
  Beinhaltet die Benutzeroberfläche des Projekts.
  app.py – Streamlit‑Anwendung, steuert Navigation, UI‑Elemente und Interaktionen
 Darstellung der EKG‑Plots, Auswahlmenüs, Buttons, usw. 


* **funktionen/**
  Sammelt spezialisierte Funktionsmodule, die unabhängig vom Backend genutzt werden können.
 peak_detection.py – Algorithmus zur Erkennung von Peaks in EKG‑Signalen (z. B. R‑Peaks)

* **data**
 Speicherort aller Rohdaten und Metadaten.
 ekg_data/ – Textdateien mit Ruhe‑ und Belastungs‑EKGs
 activity.csv – Aktivitätsdaten
 persons.json – Stammdaten der Proband*innen
 images/ - Enthält Bilder, die im Frontend angezeigt werden 

## Mögliche Projekterweiterung
Was man dann auch in die finale Abgabe noch mit einbauen könnte:
- Vergleich zweier Personen
- Mehrere EKGs pro Person als Timeline
- Datensatzabgleichung mit Normwerten 

## Die folgendes HeadUp wird für die Webseite erstellt:

![Startbild](data/images/Startseite_EKGApp.png)
![AuswahlPatient](data/images/Auswahl_Patienten.png)
![Patient](data/images/PatientenSeite.png)


