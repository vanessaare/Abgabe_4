import hashlib
import streamlit as st
import json


with open("data/users.json", "r", encoding="utf-8") as file:
    USERS = json.load(file)


# --- Daten-Helfer ---

def save_users():
    '''Speichert die Benutzerinformationen in der JSON-Datei.'''

    with open("data/users.json", "w", encoding="utf-8") as file:
        json.dump(USERS, file, indent=2)
        file.write("\n")


def normalize_username(value: str) -> str:
    '''Normalisiert den Benutzernamen, indem er in Kleinbuchstaben umgewandelt, Leerzeichen entfernt und Umlaute ersetzt werden. Nicht-alphanumerische Zeichen werden durch Unterstriche ersetzt.'''

    value = value.lower().strip()
    replacements = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}
    for old, new in replacements.items():
        value = value.replace(old, new)
    return "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in value)

def hash_password(password: str) -> str:
    '''Erstellt einen SHA-256-Hash aus dem Passwort.'''
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def is_hashed_password(value: str) -> bool:
    '''Prüft, ob der gespeicherte Wert ein SHA-256-Hash ist.'''
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)

# --- Account-Verwaltung ---

def create_patient_account(person, username=None, password=None):
    '''Erstellt einen Benutzeraccount für einen Patienten mit optionalem Benutzernamen und Passwort. Wenn diese nicht angegeben werden, werden sie automatisch generiert.'''

    if username is None:
        username = normalize_username(f"patient_{person.firstname}_{person.lastname}")

    if username in USERS:
        base_username = username
        counter = 2
        while f"{base_username}{counter}" in USERS:
            counter += 1
        username = f"{base_username}{counter}"

    if password is None:
        firstname_part = person.firstname.lower()[:3]
        lastname_part = person.lastname.lower()[:3]
        birthyear_part = str(person.date_of_birth)[-2:]
        password = f"{firstname_part}{lastname_part}{birthyear_part}"

    USERS[username] = {
        "password": hash_password(password),
        "role": "patient",
        "person_id": person.id,
    }
    save_users()
    return username, password


def delete_patient_account(person_id):
    '''Löscht den Benutzeraccount eines Patienten anhand der Personen-ID.'''

    username_to_delete = None

    for username, user in USERS.items():
        if user.get("person_id") == person_id:
            username_to_delete = username
            break

    if username_to_delete:
        del USERS[username_to_delete]
        save_users()


# --- Authentifizierung ---

def login():
    '''Rendert das Login-Formular und überprüft die Anmeldedaten.'''


    st.markdown("""
    <style>

    .main {
        background-color: #F5F7FA;
    }

    .stTextInput input {
        border-radius: 8px;
    }

    .stButton > button {
        border-radius: 10px;
        height: 45px;
        font-size: 16px;
        font-weight: 600;
    }

    </style>
    """, unsafe_allow_html=True)


    
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        
        links, mitte, rechts = st.columns([1, 2, 1])

        with mitte:
            st.image("data/images/Logo_EKGApp.png", width=450)

            st.markdown(
            "<h2 style='text-align:center;'>Willkommen bei CardioCare</h2>",
            unsafe_allow_html=True
            )

            st.markdown(
            "<p style='text-align:center; color:gray;'>"
            "Sicherer Zugriff auf Ihre Gesundheitsdaten"
            "</p>",
            unsafe_allow_html=True
        )


        username = st.text_input("Benutzername")
        password = st.text_input("Passwort", type="password")
        submit = st.button("Anmelden", use_container_width=True)

        if submit:
            if username in USERS:
                stored_password = USERS[username].get("password")
                if stored_password is None:
                    st.error("Ungültige Benutzerkonfiguration.")
                    return False

                if is_hashed_password(stored_password):
                    valid = hash_password(password) == stored_password
                else:
                    valid = password == stored_password

                if valid:
                    if not is_hashed_password(stored_password):
                        USERS[username]["password"] = hash_password(password)
                        save_users()

                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = USERS[username]["role"]
                    st.session_state.person_id = USERS[username].get("person_id")
                    st.rerun()
                else:
                    st.error("Falscher Benutzername oder Passwort")
            else:
                st.error("Falscher Benutzername oder Passwort")
        return False
    return True


def logout(force: bool = False):
    '''Rendert die Logout-Schaltfläche und setzt den Anmeldestatus zurück, wenn der Benutzer sich abmeldet.'''

    if force or st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = None
        st.session_state.person_id = None
        st.rerun()