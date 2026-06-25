import streamlit as st
import json


with open("data/users.json", "r") as file:
    USERS = json.load(file)


def login():

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:

        st.title("Login")

        username = st.text_input("Benutzername")
        password = st.text_input("Passwort", type="password")

        if st.button("Anmelden"):

            if (
                username in USERS
                and USERS[username]["password"] == password
            ):

                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = USERS[username]["role"]

                st.rerun()

            else:
                st.error("Falscher Benutzername oder Passwort")

        return False

    return True


def logout():

    if st.sidebar.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = None

        st.rerun()