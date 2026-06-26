import streamlit as st


class SessionManager:

    @staticmethod
    def init():

        defaults = {
            "page": "home",
            "selected_person": None,
            "edit_mode": False,
            "add_test_mode": False,
            "role": None,
        }

        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value