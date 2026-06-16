import streamlit as st
from backend.person import Person 
from backend.ekgdata import EKGdata


if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_person" not in st.session_state:
    st.session_state.selected_person = None


persons = Person.load_persons() #Liste mit den 6 Person-Objekten

#Navigation
def go_to_person_select():
    """Setzt die Seite auf 'select' und zeigt die Personenauswahl an."""
    print("BUTTON GEDRÜCKT")
    st.session_state.page = "select"


def set_person(person):
    """Setzt die ausgewählte Person in der Session und wechselt zur Analyse-Seite."""
    st.session_state.selected_person = person
    st.session_state.page = "analysis"


def go_home():
    """Setzt die Seite zurück auf 'home' und löscht die ausgewählte Person."""
    st.session_state.page = "home"
    st.session_state.selected_person = None

#Startseite
def home():
    """Zeigt die Startseite mit einem Willkommensgruß und einem Button zum Starten der Analyse."""
    st.title("Willkommen in Ihrer digitalen EKG-Datenbank🫀")

    st.write("Starten Sie die Analyse der Patientendaten!")

    if st.button("Analyse starten"):
        st.write("Analyse wird vorbereitet...")
        st.session_state.page = "select"
        st.rerun()



#Patient auswählen
def select_person(persons):
    """Zeigt die Seite zur Auswahl einer Testperson mit einem Dropdown-Menü und einem Button zum Fortfahren."""
    st.header("Patient:in auswählen")

    person_names = [p.get_full_name() for p in persons]

    selected_name = st.selectbox(
        "Bitte Patient:in auswählen:", 
        person_names
    )

    person = [p for p in persons if p.get_full_name() == selected_name][0]

    if st.button("Weiter"):
        set_person(person)
        st.rerun()




#Patient ansehen
def show_person(selected_person):
    """Zeigt die Seite mit den Details der ausgewählten Person, einschließlich Bild, Name, Geburtsjahr, Geschlecht und geschätzter maximaler Herzfrequenz."""
    st.header("Patient:in anzeigen")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if selected_person.picture_path:
            st.image(selected_person.get_image(), width=200)
        else:
            st.info("Kein Bild vorhanden.")
    with col2:
        st.write(f"**Name:** {selected_person.firstname} {selected_person.lastname}")
        st.write(f"**Geburtsjahr:** {selected_person.date_of_birth}")
        st.write(f"**Geschlecht:** {selected_person.gender}")
        st.write(f"**HR_max:** {selected_person.calc_max_heart_rate()} bpm")

    with col3:
        anzahl_tests = len(selected_person.ekg_tests)

        if anzahl_tests > 0:
            st.success(f"✅ {anzahl_tests} EKG-Test(s)")
        else:
            st.error("❌ Keine EKG-Daten vorhanden")
            st.stop()

    st.button("⬅ Zurück", on_click=go_home)



#EKG checken
def check_ekg_data(selected_person):
    st.header("EKG Daten überprüfen")

    if not selected_person.has_ekg_data():
        st.error("❌ Keine EKG-Daten vorhanden. Bitte einen anderen Patienten auswählen.")
        st.stop()
    st.success("EKG-Daten vorhanden!")

# Testnummer auswählen
def select_test_nr(selected_person):
    st.header("EKG Test auswählen")
    test_numbers = [f"Test {i+1}" for i in range(len(selected_person.ekg_tests))]
    selected_test = st.selectbox("Bitte Test auswählen:", test_numbers)
    return test_numbers.index(selected_test)

# EKG Analyse
def select_analysis(): 
    return st.radio(
        "Bitte Analyse auswählen:",
        ["Durchschnittspuls berechnen", "EKG-Grafik anzeigen"]
    )



def run_analysis(option, selected_person, test_nr):
    if not selected_person.ekg_tests:
        st.error("Keine EKG-Daten vorhanden")
        st.stop()
    ekg_data = selected_person.ekg_tests[test_nr]
    ekg = EKGdata(ekg_data)  # nur einmal erstellen

    if option == "Durchschnittspuls berechnen":
        try:
            bpm = ekg.estimate_hr()
            st.write(f"Der durchschnittliche Puls beträgt: **{bpm:.2f} bpm**")
        except Exception as e:
            st.error(f"Fehler beim Schätzen der Herzfrequenz: {e}")

    elif option == "EKG-Grafik anzeigen":
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📅 Testdatum**")
            st.caption(ekg_data["date"])
        with col2:
            st.markdown("**⏱️ Dauer**")
            total_min = ekg.get_duration_minutes()
            minutes = int(total_min)
            seconds = int((total_min - minutes) * 60)
            st.caption(f"{minutes} min {seconds} sek")
        try:
            total = ekg.get_duration_minutes()
            window = 4 / 60 

            start = st.slider(
                "Zeitbereich",
                min_value=0.0,
                max_value=float(total - window),
                value=0.0,
                step=1/60,  
                format="%.4f"
            )

            # Anzeige in Minuten und Sekunden
            total_seconds = start * 60
            minutes = int(total_seconds // 60)
            seconds = int(total_seconds % 60)
            st.caption(f"Position: {minutes} min {seconds} sek")

            end = start + window

            fig = ekg.plot_with_peaks_window(start_min=start, end_min=end)
            st.plotly_chart(fig, use_container_width=True)
        
        except Exception as e:
            st.error(f"Plot Fehler: {e}")


#Router
def main():
    """Steuert die Navigation zwischen den verschiedenen Seiten der Anwendung basierend auf dem aktuellen Status in der Session."""
    if st.session_state.page == "home":
        home()

    elif st.session_state.page == "select":
        select_person(persons)
        


    elif st.session_state.page == "analysis":
        person = st.session_state.selected_person

        if person is None:
            st.error("Kein Patient ausgewählt. Bitte zurückgehen.")
            st.session_state.page = "select"
            st.stop()

        show_person(person)
    

        test_nr = select_test_nr(person)  

        st.subheader("Analyse durchführen")
        option = select_analysis()

        run_analysis(option, person, test_nr)

if __name__ == "__main__":
    main()