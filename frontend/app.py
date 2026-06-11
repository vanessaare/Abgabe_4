from Abgabe_4.backend import person
from Abgabe_4.funktionen import peak_detection
import streamlit as st
from backend.person import Person 
from Abgabe_4.backend.ekgdata import EKGData, EKGdata
from peak_detection import peak_detection


persons = Person.load_persons() #Liste mit den 6 Person-Objekten
ekg_dict = selected_person.ekg_tests[0]
ekg = EKGdata(ekg_dict)

#aufpassen funktionenbennenung passt noch nicht zu unseren daten!!!
#streamlit seite aufbauen

st.set_page_config(page_title="EKG Dashboard", layout="centered") 
st.title("EKG Analyse Dashboard")



def select_person(persons):
    st.header("Patient auswählen")

    person_names = [p.get_full_name() for p in persons]

    selected_name = st.selectbox(
        "Bitte Patient auswählen:", 
        person_names
    )

    return next(
        p for p in persons 
        if p.get_full_name() == selected_name
    )




def show_person(selected_person):
    st.header("Patient anzeigen")

    col1, col2 = st.columns([1, 2])
    with col1:
        if selected_person.picture_path:
            st.image(selected_person.picture_path, width=200)
        else:
            st.info("Kein Bild vorhanden.")
    with col2:
        st.write(f"**Name:** {selected_person.firstname} {selected_person.lastname}")
        st.write(f"**Geburtsjahr:** {selected_person.date_of_birth}")
        st.write(f"**Geschlecht:** {selected_person.gender}")
        st.write(f"**HR_max:** {selected_person.calc_max_heart_rate()} bpm")




def check_ekg_data(selected_person):
    st.header("EKG Daten überprüfen")

    if not Person.has_ekg_data(selected_person):
        st.error("❌ Keine EKG-Daten vorhanden. Bitte einen anderen Patienten auswählen.")
        st.stop()
    st.success("EKG-Daten vorhanden!")



def select_analysis(): 
    st.header("Analyse auswählen")
    return st.radio(
        "Bitte Analyse auswählen:",
        ["Durchschnittspuls berechnen", "EKG-Grafik anzeigen"]
    )



def run_analysis(option, selected_person):
    if option == "Durchschnittspuls berechnen":
        st.subheader("Durchschnittspuls berechnen")

        bpm = person.calculate_heart_rate()
        st.write(f"Der durchschnittliche Puls beträgt: **{bpm:.2f} bpm**")

    elif option == "EKG-Grafik anzeigen":
        st.subheader("EKG-Grafik anzeigen")
        fig = ekg.plot_with_peaks()
        st.pyplot(fig)




