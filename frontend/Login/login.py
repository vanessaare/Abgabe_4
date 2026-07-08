import hashlib
import streamlit as st
import json


with open("data/users.json", "r", encoding="utf-8") as file:
    USERS = json.load(file)


class LoginManager:
    """Verwaltet Benutzerkonten, Login und Logout."""

    def __init__(self, users: dict):
        self.USERS = users

    # --- Daten-Helfer ---
    def save_users(self):
        '''Speichert die Benutzerinformationen in der JSON-Datei.'''
        with open("data/users.json", "w", encoding="utf-8") as file:
            json.dump(self.USERS, file, indent=2)
            file.write("\n")

    def normalize_username(self, value: str) -> str:
        value = value.lower().strip()
        replacements = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}
        for old, new in replacements.items():
            value = value.replace(old, new)
        return "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in value)

    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def is_hashed_password(self, value: str) -> bool:
        return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)

    # --- Account-Verwaltung ---
    def create_patient_account(self, person, username=None, password=None):
        if username is None:
            username = self.normalize_username(f"patient_{person.firstname}_{person.lastname}")

        if username in self.USERS:
            base_username = username
            counter = 2
            while f"{base_username}{counter}" in self.USERS:
                counter += 1
            username = f"{base_username}{counter}"

        if password is None:
            firstname_part = person.firstname.lower()[:3]
            lastname_part = person.lastname.lower()[:3]
            birthyear_part = str(person.date_of_birth)[-2:]
            password = f"{firstname_part}{lastname_part}{birthyear_part}"

        self.USERS[username] = {
            "password": self.hash_password(password),
            "role": "patient",
            "person_id": person.id,
        }
        self.save_users()
        return username, password

    def delete_patient_account(self, person_id):
        username_to_delete = None
        for username, user in self.USERS.items():
            if user.get("person_id") == person_id:
                username_to_delete = username
                break
        if username_to_delete:
            del self.USERS[username_to_delete]
            self.save_users()

    # --- Authentifizierung ---
    def login(self):
        st.markdown("""
        <style>
        .main { background-color: #F5F7FA; }
        .stTextInput input { border-radius: 8px; }
        .stButton > button { border-radius: 10px; height: 45px; font-size: 16px; font-weight: 600; }
        </style>
        """, unsafe_allow_html=True)

        if "logged_in" not in st.session_state:
            st.session_state.logged_in = False

        if not st.session_state.logged_in:
            links, mitte, rechts = st.columns([1, 2, 1])
            with rechts:
                st.image("data/images/Logo_EKGApp.png", width=300)
            with mitte:
    
                st.markdown("<h2 style='text-align:center;'>Willkommen bei CardioCare</h2>", unsafe_allow_html=True)
                st.markdown("<p style='text-align:center; color:gray;'>Sicherer Zugriff auf Ihre Gesundheitsdaten</p>", unsafe_allow_html=True)

            username = st.text_input("Benutzername")
            password = st.text_input("Passwort", type="password")
            submit = st.button("Anmelden", width="stretch")

            if submit:
                if username in self.USERS:
                    stored_password = self.USERS[username].get("password")
                    if stored_password is None:
                        st.error("Ungültige Benutzerkonfiguration.")
                        return False

                    if self.is_hashed_password(stored_password):
                        valid = self.hash_password(password) == stored_password
                    else:
                        valid = password == stored_password

                    if valid:
                        if not self.is_hashed_password(stored_password):
                            self.USERS[username]["password"] = self.hash_password(password)
                            self.save_users()

                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.role = self.USERS[username]["role"]
                        st.session_state.person_id = self.USERS[username].get("person_id")
                        st.rerun()
                    else:
                        st.error("Falscher Benutzername oder Passwort")
                else:
                    st.error("Falscher Benutzername oder Passwort")
            return False
        return True

    def logout(self, force: bool = False):
        if force or st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.role = None
            st.session_state.person_id = None
            st.rerun()


# Instantiate a module-level manager and provide function wrappers for compatibility
manager = LoginManager(USERS)