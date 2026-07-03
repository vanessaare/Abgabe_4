import streamlit as st 
from backend.loader import load_test
from backend.person import Person
from backend.funktionen.hrv import calculate_hrv_rmssd

# --- Analyse-Verwaltung ---

class AnalysisManager:
    '''Verwaltet die Analyse von EKG-Daten und die Interaktion mit der Benutzeroberfläche.'''

    def run_analysis(self, person, test_nr, persons=None):
        """Führt die gewählte EKG-Analyse durch, visualisiert Ergebnisse und speichert Berechnungen."""

        ekg_dict = person.ekg_tests[test_nr]
        ekg      = load_test(ekg_dict)

        option = st.radio(
            "Analyse auswählen:",
            ["Durchschnittspuls", "EKG-Grafik", "HRV"],
            key=f"analysis_radio_{person.id}_{test_nr}",
        )

        if option == "Durchschnittspuls":
            try:
                avg_hr = ekg.estimate_hr()
                ekg_dict["average_hr"] = float(avg_hr)
                if persons is not None:
                    for p in persons:
                        if p.id == person.id:
                            p.ekg_tests = person.ekg_tests
                            break
                    Person.save_persons(persons)
                st.write(f"Durchschnittlicher Puls: **{avg_hr:.2f} bpm**")
            except Exception as e:
                st.error(f"Fehler: {e}")

        elif option == "EKG-Grafik":
            col1, col2 = st.columns(2)
            col1.caption(f"📅 {ekg_dict['date']}")
            total_min = ekg.get_duration_minutes()
            col2.caption(f"⏱️ {int(total_min)}m {int((total_min % 1) * 60)}s")

            total_sec  = int(total_min * 60)
            window_sec = 60 if ekg_dict.get("result_link", "").endswith(".fit") else 4
            start_sec  = st.slider("Zeitbereich", 0, max(0, total_sec - window_sec), 0)
            st.caption(f"Position: {start_sec // 60}m {start_sec % 60}s")

            try:
                fig = ekg.plot_with_peaks_window(start_sec / 60, (start_sec + window_sec) / 60)
                st.plotly_chart(fig, use_container_width=True, key=f"ekg_{start_sec}")
            except Exception as e:
                st.error(f"Plot Fehler: {e}")

        elif option == "HRV":
            try:
                rmssd = calculate_hrv_rmssd(ekg)
                if rmssd is not None:
                    ekg_dict["hrv_rmssd"] = float(rmssd)
                    if persons is not None:
                        for p in persons:
                            if p.id == person.id:
                                p.ekg_tests = person.ekg_tests
                                break
                        Person.save_persons(persons)
                    st.write(f"HRV (RMSSD): **{rmssd:.2f} ms**")
                else:
                    st.warning("Nicht genügend Peaks für HRV-Berechnung.")
            except Exception as e:
                st.error(f"Fehler: {e}")