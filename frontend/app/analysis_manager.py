import streamlit as st 
from backend.loader import load_test
from funktionen.hrv import calculate_hrv_rmssd

class AnalysisManager:


    def run_analysis(self, person, test_nr):

        ekg_dict = person.ekg_tests[test_nr]
        ekg      = load_test(ekg_dict)

        option = st.radio("Analyse auswählen:", ["Durchschnittspuls", "EKG-Grafik", "HRV"])

        if option == "Durchschnittspuls":
            try:
                st.write(f"Durchschnittlicher Puls: **{ekg.estimate_hr():.2f} bpm**")
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
                    st.write(f"HRV (RMSSD): **{rmssd:.2f} ms**")
                else:
                    st.warning("Nicht genügend Peaks für HRV-Berechnung.")
            except Exception as e:
                st.error(f"Fehler: {e}")