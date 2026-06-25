import os
import datetime
import streamlit as st
from backend.person import Person
from backend.loader import load_test
from funktionen.hrv import calculate_hrv_rmssd
from frontend.login import login, logout, create_patient_account

persons = Person.load_persons()

# --- Navigation ---

def go_home():
    st.session_state.page = "home"
    st.session_state.selected_person = None

def set_person(person):
    st.session_state.selected_person = person
    st.session_state.page = "analysis"


def delete_person(person):
    global persons
    persons = [p for p in persons if p.id != person.id]
    Person.save_persons(persons)
    st.session_state.page = "home"
    st.session_state.selected_person = None
    st.success(f"✅ Person {person.get_full_name()} wurde gelöscht.")
    st.rerun()


# --- Neue Person hinzufügen ---

def add_person_form():
    st.subheader("➕ Neue Person hinzufügen")
    with st.form("add_person"):
        col1, col2 = st.columns(2)
        firstname   = col1.text_input("Vorname")
        lastname    = col2.text_input("Nachname")
        dob         = col1.number_input("Geburtsjahr", min_value=1900, max_value=datetime.date.today().year, value=1990)
        gender      = col2.selectbox("Geschlecht", ["Male", "Female"])
        picture     = st.file_uploader("Bild (optional)", type=["jpg", "jpeg", "png", "webp"])
        submitted   = st.form_submit_button("Person speichern")

    if submitted:
        if not firstname or not lastname:
            st.error("Vor- und Nachname sind Pflichtfelder.")
            return

        new_id = Person.next_person_id(persons)

        # Bild speichern
        pic_path = "data/images/default.webp"
        if picture:
            ext      = picture.name.split(".")[-1]
            pic_path = f"data/images/Person{new_id}_{gender.lower()}.{ext}"
            os.makedirs("data/images", exist_ok=True)
            with open(pic_path, "wb") as f:
                f.write(picture.read())

        new_person = Person(new_id, int(dob), firstname, lastname, pic_path, [], gender)
        persons.append(new_person)
        Person.save_persons(persons)
        username, password = create_patient_account(new_person)
        st.success(f"✅ {new_person.get_full_name()} wurde gespeichert.\nLogin: {username}\nPasswort: {password}")
        st.rerun()


# --- Person editieren ---

def edit_person_form(person):
    st.subheader("✏️ Person editieren")
    with st.form("edit_person"):
        col1, col2 = st.columns(2)
        firstname = col1.text_input("Vorname",   value=person.firstname)
        lastname  = col2.text_input("Nachname",  value=person.lastname)
        dob       = col1.number_input("Geburtsjahr", min_value=1900,
                                      max_value=datetime.date.today().year,
                                      value=person.date_of_birth)
        gender    = col2.selectbox("Geschlecht", ["Male", "Female"],
                                   index=0 if person.gender == "Male" else 1)
        picture   = st.file_uploader("Neues Bild (optional)", type=["jpg", "jpeg", "png", "webp"])
        submitted = st.form_submit_button("Änderungen speichern")

    if submitted:
        person.firstname     = firstname
        person.lastname      = lastname
        person.date_of_birth = int(dob)
        person.gender        = gender

        if picture:
            ext           = picture.name.split(".")[-1]
            pic_path      = f"data/images/Person{person.id}_{gender.lower()}.{ext}"
            os.makedirs("data/images", exist_ok=True)
            with open(pic_path, "wb") as f:
                f.write(picture.read())
            person.picture_path = pic_path

        Person.save_persons(persons)
        st.success("✅ Änderungen gespeichert.")
        st.session_state.edit_mode = False
        st.rerun()


# --- Neuen Test hinzufügen ---

def add_test_form(person):
    st.subheader("➕ Neuen Test hinzufügen")
    with st.form("add_test"):
        date     = st.date_input("Testdatum", value=datetime.date.today())
        file     = st.file_uploader("Datendatei (.txt oder .fit)", type=["txt", "fit"])
        submitted = st.form_submit_button("Test speichern")

    if submitted:
        if not file:
            st.error("Bitte eine Datei hochladen.")
            return

        ext      = "fit" if file.name.endswith(".fit") else "txt"
        new_id   = Person.next_test_id(persons)
        save_dir = "data/ekg_data"
        os.makedirs(save_dir, exist_ok=True)
        save_path = f"{save_dir}/{person.id:02d}_{new_id}.{ext}"

        with open(save_path, "wb") as f:
            f.write(file.read())

        person.ekg_tests.append({
            "id":          new_id,
            "date":        str(date),
            "result_link": save_path,
        })
        Person.save_persons(persons)
        st.success(f"✅ Test {new_id} gespeichert ({ext.upper()}).")
        st.rerun()


# --- Seiten ---

def home():
    st.title("Willkommen in Ihrer digitalen EKG-Datenbank 🫀")
    if st.button("Analyse starten"):
        st.session_state.page = "select"
        st.rerun()
    if st.session_state.role == "patient":
        st.info("Herzlich Willkommen! " \
        "Hier können Sie Ihre EKG-Daten einsehen. " \
        "Bitte wenden Sie sich an das medizinische Personal, um neue Tests hinzuzufügen oder Ihre Daten zu bearbeiten.")


def select_person():
    st.header("Patient:in auswählen")

    if not persons:
        st.info("Noch keine Personen vorhanden.")
        return

    names = [p.get_full_name() for p in persons]

    selected_name = st.selectbox("Bitte Patient:in auswählen:", names)

    selected_person = next(p for p in persons if p.get_full_name() == selected_name)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Weiter"):
            set_person(selected_person)
            st.rerun()

    with col2:
        if st.session_state.role != "patient":
            if st.button("🗑️"):
                persons.remove(selected_person)
                st.success(f"✅ {selected_person.get_full_name()} wurde gelöscht.")
                st.rerun()

    if st.session_state.get("role") != "patient":
        with st.expander("➕ Neue Person hinzufügen"):
            add_person_form()

def show_person(person):
    st.header("Patient:in anzeigen")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if person.picture_path and os.path.exists(person.picture_path):
            st.image(person.get_image(), width=200)
    with col2:
        st.write(f"**Name:** {person.firstname} {person.lastname}")
        st.write(f"**Geburtsjahr:** {person.date_of_birth}")
        st.write(f"**Geschlecht:** {person.gender}")
        st.write(f"**HR_max:** {person.calc_max_heart_rate()} bpm")
    with col3:
        n = len(person.ekg_tests)
        if n:
            st.success(f"✅ {n} EKG-Test(s)")
        else:
            st.warning("⚠️ Keine EKG-Daten")

    # Buttons: Zurück | Editieren | Test hinzufügen
    st.button("⬅ Zurück", on_click=go_home)


    if st.session_state.get("role") != "patient":
        with st.expander("✏️ Person editieren"):
            edit_person_form(person)

        with st.expander("➕ Test hinzufügen"):
            add_test_form(person)
            if not person.has_ekg_data():
                st.stop()
    else:
        st.info("Sie haben keine Berechtigung, Daten zu bearbeiten oder neue Tests hinzuzufügen.")


def select_test_nr(person):
    labels   = [f"Test {i+1}" for i in range(len(person.ekg_tests))]
    selected = st.selectbox("Bitte Test auswählen:", labels)
    return labels.index(selected)


def run_analysis(person, test_nr):
    ekg_dict = person.ekg_tests[test_nr]
    ekg      = load_test(ekg_dict)

    option = st.radio("Analyse auswählen:", ["Durchschnittspuls", "EKG-Grafik", "HRV"])

    if option == "Durchschnittspuls":
        try:
            st.write(f"Durchschnittlicher Puls: **{ekg.estimate_hr():.2f} bpm**")
        except Exception as e:
            st.error(f"Fehler: {e}")

    elif option == "EKG-Grafik":
        col1, col2 = st.columns(2)
        col1.caption(f"📅 {ekg_dict['date']}")
        total_min = ekg.get_duration_minutes()
        col2.caption(f"⏱️ {int(total_min)}m {int((total_min % 1) * 60)}s")

        total_sec  = int(total_min * 60)
        window_sec = 60 if ekg_dict.get("result_link", "").endswith(".fit") else 4
        start_sec  = st.slider("Zeitbereich", 0, max(0, total_sec - window_sec), 0)
        st.caption(f"Position: {start_sec // 60}m {start_sec % 60}s")

        try:
            fig = ekg.plot_with_peaks_window(start_sec / 60, (start_sec + window_sec) / 60)
            st.plotly_chart(fig, use_container_width=True, key=f"ekg_{start_sec}")
        except Exception as e:
            st.error(f"Plot Fehler: {e}")

    elif option == "HRV":
        try:
            rmssd = calculate_hrv_rmssd(ekg)
            if rmssd is not None:
                st.write(f"HRV (RMSSD): **{rmssd:.2f} ms**")
            else:
                st.warning("Nicht genügend Peaks für HRV-Berechnung.")
        except Exception as e:
            st.error(f"Fehler: {e}")


# --- Router ---

def main():
    """Steuert die Navigation zwischen den verschiedenen Seiten der Anwendung basierend auf dem aktuellen Status in der Session."""

    if not login():
        st.stop()
    logout()

    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "selected_person" not in st.session_state:
        st.session_state.selected_person = None
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False
    if "add_test_mode" not in st.session_state:
        st.session_state.add_test_mode = False

    if st.session_state.get("role") == "patient":
        person_id = st.session_state.get("person_id")
        if person_id is not None:
            matching_person = next((p for p in persons if p.id == person_id), None)
            if matching_person is not None:
                st.session_state.selected_person = matching_person
                if st.session_state.page == "home":
                    st.session_state.page = "analysis"

    st.sidebar.write(
        f"Angemeldet als: {st.session_state.username}")

    page = st.session_state.page

    if page == "home":
        home()

    elif page == "select":
        select_person()

    elif page == "analysis":

        person = st.session_state.selected_person

        if person is None:
            st.session_state.page = "select"
            st.rerun()

        show_person(person)

        if person.has_ekg_data() and not st.session_state.get("edit_mode") and not st.session_state.get("add_test_mode"):

            st.subheader("Analyse durchführen")
            test_nr = select_test_nr(person)
            run_analysis(person, test_nr)