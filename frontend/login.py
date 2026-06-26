import streamlit as st
import json


with open("data/users.json", "r", encoding="utf-8") as file:
    USERS = json.load(file)


def save_users():
    with open("data/users.json", "w", encoding="utf-8") as file:
        json.dump(USERS, file, indent=2)
        file.write("\n")


def normalize_username(value: str) -> str:
    value = value.lower().strip()
    replacements = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}
    for old, new in replacements.items():
        value = value.replace(old, new)
    return "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in value)


def create_patient_account(person, username=None, password=None):
    if username is None:
        username = normalize_username(f"patient_{person.firstname}_{person.lastname}")

    if username in USERS:
        base_username = username
        counter = 2
        while f"{base_username}{counter}" in USERS:
            counter += 1
        username = f"{base_username}{counter}"

    if password is None:
        password = f"{person.firstname.lower()[:3]}{person.lastname.lower()[:4]}{person.id}"

    USERS[username] = {
        "password": password,
        "role": "patient",
        "person_id": person.id,
    }
    save_users()
    return username, password


def delete_patient_account(person_id):
    username_to_delete = None

    for username, user in USERS.items():
        if user.get("person_id") == person_id:
            username_to_delete = username
            break

    if username_to_delete:
        del USERS[username_to_delete]
        save_users()




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
                st.session_state.person_id = USERS[username].get("person_id")

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
        st.session_state.person_id = None

        st.rerun()
