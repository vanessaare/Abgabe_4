import streamlit as st

from backend.person import Person
from funktionen.filter_persons import filter_persons

class PersonManager:

    def __init__(self):
        self.persons = Person.load_persons()

    def get_filtered(self, name):
        return filter_persons(self.persons, name)


    def delete_person(self, person):
        self.persons = [p for p in self.persons if p.id != person.id]
        Person.save_persons(self.persons)

        st.session_state.page = "home"
        st.session_state.selected_person = None

        st.success(f"✅ Person {person.get_full_name()} wurde gelöscht.")
        st.rerun()

