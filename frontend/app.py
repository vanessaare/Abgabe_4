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
    print("BUTTON GEDRÜCKT")
    st.session_state.page = "select"


def set_person(person):
    st.session_state.selected_person = person
    st.session_state.page = "analysis"


def go_home():
    st.session_state.page = "home"
    st.session_state.selected_person = None

#Startseite
def home():
    st.title("Willkommen in Ihrer digitalen EKG-Datenbank🫀")

    st.write("Starten Sie die Analyse der Patientendaten!")

    if st.button("Auf los gehts los🚀"):
        st.write("BUTTON WURDE GEDRÜCKT")
        st.session_state.page = "select"
        st.rerun()



#Patient auswählen
def select_person(persons):
    st.header("Patient:in auswählen")

    person_names = [p.get_full_name() for p in persons]

    selected_name = st.selectbox(
        "Bitte Patient:in auswählen:", 
        person_names
    )

    person = [p for p in persons if p.get_full_name() == selected_name][0]

    if st.button("Weiter"):
        set_person(person)



#Patient ansehen
def show_person(selected_person):
    st.header("Patient:in anzeigen")

    col1, col2 = st.columns([1, 2])
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

    st.button("⬅ Zurück", on_click=go_home)



#EKG checken
def check_ekg_data(selected_person):
    st.header("EKG Daten überprüfen")

    if not selected_person.has_ekg_data():
        st.error("❌ Keine EKG-Daten vorhanden. Bitte einen anderen Patienten auswählen.")
        st.stop()
    st.success("EKG-Daten vorhanden!")


# EKG Analyse
def select_analysis(): 
    st.header("Analyse auswählen")
    return st.radio(
        "Bitte Analyse auswählen:",
        ["Durchschnittspuls berechnen", "EKG-Grafik anzeigen"]
    )



def run_analysis(option, selected_person):
    if not selected_person.ekg_tests:
        st.error("Keine EKG-Daten vorhanden")
        st.stop()
    
    ekg_data = selected_person.ekg_tests[0]

    if option == "Durchschnittspuls berechnen":
        try:
            ekg = EKGdata(ekg_data)
            bpm = ekg.estimate_hr()
            st.write(f"Der durchschnittliche Puls beträgt: **{bpm:.2f} bpm**")

        except Exception as e:
            st.error(f"Fehler beim Schätzen der Herzfrequenz: {e}")
    

    elif option == "EKG-Grafik anzeigen":
        try:
            ekg = EKGdata(ekg_data)
            fig = ekg.plot_with_peaks()
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Plot Fehler: {e}")
        


#Router
def main():
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
        check_ekg_data(person)

        option = select_analysis()
        run_analysis(option, person)

if __name__ == "__main__":
    main()