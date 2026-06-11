import streamlit as st
from backend.person import Person 
from backend.ekgdata import EKGdata


persons = Person.load_persons() #Liste mit den 6 Person-Objekten



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
            st.image(selected_person.get_image(), width=200)
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

        ekg = EKGdata(selected_person.ekg_tests[0])
        bpm = ekg.estimate_hr()

        st.write(f"Der durchschnittliche Puls beträgt: **{bpm:.2f} bpm**")

    elif option == "EKG-Grafik anzeigen":
        st.subheader("EKG-Grafik anzeigen")

        ekg_dict = selected_person.ekg_tests[0]
        ekg = EKGdata(ekg_dict)

        fig = ekg.plot_with_peaks()
        st.plotly_chart(fig)
        

def main():
    persons = Person.load_persons()

    selected_person = select_person(persons)
    show_person(selected_person)

    check_ekg_data(selected_person)

    option = select_analysis()
    run_analysis(option, selected_person)


main()