# Abgabe_4

**Teilnehmerinnen:** Melanie Pfusterer, Lisa Raffler, Vanessa Reich

Das Projekt erstellt eine mithilfe von Streamlit eine Webseite, die als eine Art Datenbank dienen soll. 
In der man, verschiedene Probanden auswählen kann, diese dann angezeigen kann und weitere Attribute die zu diesen gehören ebenso zeigen. 
Desweiteren wir aus den  EKG Daten (Ruhe-/Belastungsdaten)  ein **EKG Diagramm** erstellt. Die Werte werden aus den Dateien (*01_Ruhe.txt; 02_Ruhe.txt, 03_Ruhe.txt, 04_Belastung.txt, 05_Belastung.txt*) geladen, verarbeitet und anschließend in auf der Webseite für die Einzelnen Probanden dargestellt.

Zur Installation des Projekts wird pip verwendet.

## Um die Webseite anzeigen zu lassen, muss folgendermaßen vorgegangen werden:

1. Installation der Abhängigkeiten
   **->** pip install -r requirements.txt

2. Projekt starten
   **->** streamlit run main.py

## Was macht das Projekt?

1. Leistungsdaten werden aus einer Datei (*activity.csv*) geladen und aussortiert.
2. Für verschiedene Zeitdauern wird die maximale durchschnittliche Leistung berechnet.
3. Die Ergebnisse werden in einem DataFrame gespeichert.
4. Die Power Curve wird als Diagramm dargestellt.
5. Die Grafik wird gespeichert.

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


