import streamlit as st

# --- Navigation ---

class Navigation:
    '''Verwaltet die Navigation innerhalb der Streamlit-App.'''

    @staticmethod
    def go_home():
        """Setzt die App-Navigation auf die Startseite zurück und leert die Patientenauswahl."""

        st.session_state.page = "home"
        st.session_state.selected_person = None

    @staticmethod
    def go_select():
        '''Setzt die App-Navigation auf die Patientenauswahl zurück.'''

        st.session_state.page = "select"

    @staticmethod
    def set_person(person):
        '''Setzt die ausgewählte Person in der Session und navigiert zur Analyse-Seite.'''

        st.session_state.selected_person = person
        st.session_state.page = "analysis"

