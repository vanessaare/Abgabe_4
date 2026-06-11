import streamlit as st
import read_data  # Importiert deine Funktionen

# Überschriften
st.write("# EKG APP")
st.write("## Versuchsperson auswählen")

# 1. Daten laden
person_dict = read_data.load_person_data()

# 2. Liste holen
# WICHTIG: Hier muss die Variable stehen, die die Namen aus dem JSON enthält!
user_list = read_data.get_person_list(person_dict)

# 3. Auswahlbox
if user_list:
    current_user = st.selectbox(
        'Versuchsperson',
        options = user_list, # <--- DAS MUSS HIER STEHEN
        key="sbVersuchsperson"
    )
    st.success(f"Nutzer {current_user} geladen.")
else:
    st.error("Keine User in der JSON-Datei gefunden!")