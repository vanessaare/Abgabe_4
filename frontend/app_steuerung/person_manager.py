import streamlit as st

from backend.models.person import Person
from frontend.Login.login import manager
from backend.utils.filter_persons import filter_persons

# --- Personen-Verwaltung ---

class PersonManager:
    '''Verwaltet die Personenliste, Filterung und Löschung von Personen innerhalb der Streamlit-App.'''

    def __init__(self):
        '''initialisiert die PersonManager-Klasse und lädt die Personen aus der Datenbank.'''

        self.persons = Person.load_persons()

    def get_filtered(self, name):
        '''Filtert die Personenliste basierend auf dem angegebenen Namen und gibt die gefilterte Liste zurück.'''

        return filter_persons(self.persons, name)

    def delete_person(self, person):
        '''Löscht eine Person aus der Personenliste und aktualisiert die Datenbank.'''

        self.persons = [p for p in self.persons if p.id != person.id]
        Person.save_persons(self.persons)
        manager.delete_patient_account(person.id)

        st.session_state.page = "home"
        st.session_state.selected_person = None

        st.success(f"✅ Person {person.get_full_name()} wurde gelöscht.")
        st.rerun()