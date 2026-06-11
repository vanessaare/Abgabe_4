import streamlit as st
from backend.person import Person 
from Abgabe_4.backend.ekgdata import EKGData
from backend.utils.read_data import load_all_persons



#Daten laden
#personen hier laden!!!
#aufpassen funktionenbennenung passt noch nicht zu unseren daten!!!
#streamlit seite aufbauen
st.set_page_config(page_title="EKG Dashboard", layout="centered") 
st.title("EKG Analyse Dashboard")

#1. Personendaten laden 
st.header("Patient auswählen")

person_names = [f"{p.firstname} {p.lastname}" for p in persons]
selected_name = st.selectbox("Bitte Patient auswählen:", person_names)
#genau ein Patient wird ausgewählt 
selected_person = next((p for p in persons if f"{p.firstname} {p.lastname}" == selected_name), None)

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
    st.write(f"**HR_max:** {selected_person.hr_max}")


#EKG Daten anzeigen
st.header("EKG Daten überprüfen")
if person.has_ekg_data():
    st.success("EKG-Daten vorhanden!")
    st.error("❌ Keine EKG-Daten vorhanden. Bitte einen anderen Patienten auswählen.")
    st.stop()
#Auswahl der EKG Daten 
st.header("Analyse auswählen")
option = st.radio(
    "Bitte Analyse auswählen:",
    ["Durchschnittspuls berechnen", "EKG-Grafik anzeigen"]
)

if option == "Durchschnittspuls berechnen":
    st.subheader("Durchschnittspuls berechnen")
    avg_hr = selected_person.calculate_heart_rate()
    st.write(f"Der durchschnittliche Puls beträgt: **{avg_hr:.2f} bpm**")

elif option == "EKG-Grafik anzeigen":
    st.subheader("EKG-Grafik anzeigen")
    fig = plot_with_peaks(selected_person)
    st.pyplot(fig)




