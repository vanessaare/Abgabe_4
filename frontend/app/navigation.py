import streamlit as st


class Navigation:
    @staticmethod
    def go_home():
        st.session_state.page = "home"
        st.session_state.selected_person = None

    @staticmethod
    def go_select():
        st.session_state.page = "select"

    @staticmethod
    def set_person(person):
        st.session_state.selected_person = person
        st.session_state.page = "analysis"

