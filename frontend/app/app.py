import os
import datetime
import streamlit as st

from backend.person import Person
from frontend.login import login, logout, create_patient_account

from .person_manager import PersonManager
from .analysis_manager import AnalysisManager
from .navigation import Navigation
from .session import SessionManager


class App:

    def __init__(self):
        self.person_manager = PersonManager()
        self.analysis_manager = AnalysisManager()

    def home(self):
        st.title("Digitale EKG-Datenbank 🫀")
        st.subheader(f"Herzlich Willkommen, {st.session_state.username}!")


        if st.session_state.role != "patient":
            st.write("Was möchten Sie tun?")

            col2, col1 = st.columns(2)

            with col1:
                if st.button(
                    "➕ Neuen Patienten hinzufügen",
                    key="home_add_patient",
                    use_container_width=True,
                    type="primary"
                ):
                    st.session_state.page = "add_person_form"
                    st.rerun()

            with col2:
                if st.button(
                    "🔍 Patienten suchen",
                    key="home_search_patient",
                    use_container_width=True
                ):
                    st.session_state.page = "select"
                    st.rerun()

            col3, col4 = st.columns(2)

            with col3:
                if st.button(
                    "📊 Statistiken",
                    key="home_stats",
                    use_container_width=True
                ):
                    st.info("Statistik-Seite folgt.")

            with col4:
                if st.button(
                    "⚙️ Einstellungen",
                    key="home_settings",
                    use_container_width=True
                ):
                    st.info("Einstellungen folgen.")

            

        else:

            st.info(
                "Hier können Sie Ihre eigenen EKG-Daten und Analysen einsehen. "
                "Neue Tests oder Änderungen können ausschließlich vom medizinischen Personal vorgenommen werden."
            )

            if st.button(
                "🫀 Meine EKG-Daten anzeigen",
                key="home_patient_data",
                use_container_width=True,
                type="primary"
            ):
                # Der eingeloggte Patient sollte bereits im Login
                # als selected_person gespeichert werden.
                st.session_state.page = "analysis"
                st.rerun()

    # --- Person auswählen ---

    def select_person(self):
        st.subheader("🔍 Filter")

        st.button("⬅ Zurück", key="select_back", on_click=Navigation.go_home)

        name_filter = st.text_input("Name suchen")

        filtered = self.person_manager.get_filtered(
            name_filter
        )

        if not filtered:
            st.warning("Keine passenden Patienten gefunden.")
        else:
            st.header("Patient:in auswählen")

            names = [p.get_full_name() for p in filtered]
            selected_name = st.selectbox("Bitte Patient:in auswählen:", names)
            selected_person = next(p for p in filtered if p.get_full_name() == selected_name)

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Weiter", key="select_continue"):
                    Navigation.set_person(selected_person)
                    st.rerun()

            with col2:
                if st.session_state.role != "patient":
                    if st.button("🗑️", key="select_delete"):
                        self.person_manager.delete_person(selected_person)

        if st.session_state.get("role") != "patient":
            with st.expander("➕ Neue Person hinzufügen"):
                self.add_person_form()


    # --- Neue Person hinzufügen ---

    def add_person_form(self):
        st.subheader("➕ Neue Person hinzufügen")
        st.button("⬅ Zurück", key="add_person_back", on_click=Navigation.go_home)
        with st.form("add_person"):
            col1, col2 = st.columns(2)
            firstname = col1.text_input("Vorname")
            lastname = col2.text_input("Nachname")
            dob = col1.number_input(
                "Geburtsjahr",
                min_value=1900,
                max_value=datetime.date.today().year,
                value=1990,
            )
            gender = col2.selectbox("Geschlecht", ["Male", "Female"])
            picture = st.file_uploader("Bild (optional)", type=["jpg", "jpeg", "png", "webp"])
            submitted = st.form_submit_button("Person speichern")
    

        if submitted:
            if not firstname or not lastname:
                st.error("Vor- und Nachname sind Pflichtfelder.")
                return

            new_id = Person.next_person_id(self.person_manager.persons)
            pic_path = "data/images/default.webp"

            if picture:
                ext = picture.name.split(".")[-1]
                pic_path = f"data/images/Person{new_id}_{gender.lower()}.{ext}"
                os.makedirs("data/images", exist_ok=True)
                with open(pic_path, "wb") as f:
                    f.write(picture.read())

            new_person = Person(new_id, int(dob), firstname, lastname, pic_path, [], gender)
            self.person_manager.persons.append(new_person)
            Person.save_persons(self.person_manager.persons)

            username, password = create_patient_account(new_person)
            st.success(
                f"✅ {new_person.get_full_name()} wurde gespeichert.\nLogin: {username}\nPasswort: {password}"
            )

            col1, col2 = st.columns(2)

            with col1:
                st.button(
                    "Zurück zur Startseite",
                    key="add_person_back_to_home",
                    on_click=self._go_home,
                )

            with col2:
                st.button(
                    "Weiteren Patienten hinzufügen",
                    key="add_person_add_another",
                    on_click=self._show_add_person_form,
                )

    # --- Person anzeigen ---

    def show_person(self, person):
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

        st.button("⬅ Zurück", key="show_person_back", on_click=self._go_home)

        if st.session_state.get("role") != "patient":
            with st.expander("✏️ Person editieren"):
                self.edit_person_form(person)

            with st.expander("➕ Test hinzufügen"):
                self.add_test_form(person)
                if not person.has_ekg_data():
                    st.stop()
        else:
            st.info("Sie haben keine Berechtigung, Daten zu bearbeiten oder neue Tests hinzuzufügen.")

    # --- Test auswählen ---

    def select_test_nr(self, person):
        labels = [f"Test {i+1}" for i in range(len(person.ekg_tests))]

        if not labels:
            st.info("Keine Tests vorhanden.")
            return None

        selected = st.selectbox("Bitte Test auswählen:", labels)
        idx = labels.index(selected)

        if st.session_state.get("role") != "patient":
            if st.button("🗑️ Löschen", key="select_test_delete"):
                del person.ekg_tests[idx]
                Person.save_persons(self.person_manager.persons)
                st.success(f"{selected} wurde gelöscht.")
                st.rerun()

        return idx

    def _go_home(self):
        st.session_state.page = "home"
        st.rerun()

    def _show_add_person_form(self):
        st.session_state.page = "add_person_form"
        st.rerun()

    # --- Person editieren ---

    def edit_person_form(self, person):
        st.subheader("✏️ Person editieren")

        with st.form("edit_person"):
            col1, col2 = st.columns(2)
            firstname = col1.text_input("Vorname", value=person.firstname)
            lastname = col2.text_input("Nachname", value=person.lastname)
            dob = col1.number_input(
                "Geburtsjahr",
                min_value=1900,
                max_value=datetime.date.today().year,
                value=person.date_of_birth,
            )
            gender = col2.selectbox(
                "Geschlecht",
                ["Male", "Female"],
                index=0 if person.gender == "Male" else 1,
            )
            picture = st.file_uploader("Neues Bild (optional)", type=["jpg", "jpeg", "png", "webp"])
            submitted = st.form_submit_button("Änderungen speichern")

        if submitted:
            person.firstname = firstname
            person.lastname = lastname
            person.date_of_birth = int(dob)
            person.gender = gender

            if picture:
                ext = picture.name.split(".")[-1]
                pic_path = f"data/images/Person{person.id}_{gender.lower()}.{ext}"
                os.makedirs("data/images", exist_ok=True)
                with open(pic_path, "wb") as f:
                    f.write(picture.read())
                person.picture_path = pic_path

            Person.save_persons(self.person_manager.persons)
            st.success("✅ Änderungen gespeichert.")
            st.session_state.edit_mode = False
            st.rerun()

    # --- Neuen Test hinzufügen ---

    def add_test_form(self, person):
        st.subheader("➕ Neuen Test hinzufügen")

        with st.form("add_test"):
            date = st.date_input("Testdatum", value=datetime.date.today())
            file = st.file_uploader("Datendatei (.txt oder .fit)", type=["txt", "fit"])
            submitted = st.form_submit_button("Test speichern")

        if submitted:
            if not file:
                st.error("Bitte eine Datei hochladen.")
                return

            ext = "fit" if file.name.endswith(".fit") else "txt"
            new_id = Person.next_test_id(self.person_manager.persons)
            save_dir = "data/ekg_data"
            os.makedirs(save_dir, exist_ok=True)
            save_path = f"{save_dir}/{person.id:02d}_{new_id}.{ext}"

            with open(save_path, "wb") as f:
                f.write(file.read())

            person.ekg_tests.append(
                {
                    "id": new_id,
                    "date": str(date),
                    "result_link": save_path,
                }
            )
            Person.save_persons(self.person_manager.persons)
            st.success(f"✅ Test {new_id} gespeichert ({ext.upper()}).")
            st.rerun()

    # --- Router ---

    def main(self):
        """Steuert die Navigation zwischen den verschiedenen Seiten der Anwendung basierend auf dem aktuellen Status in der Session."""

        SessionManager.init()

        if not login():
            st.stop()

        logout()

        st.sidebar.write(f"Angemeldet als: {st.session_state.username}")

        page = st.session_state.page

        if page == "home":
            self.home()
        elif page == "select":
            self.select_person()
        elif page == "add_person_form":
            self.add_person_form()
        elif page == "analysis":
            person = st.session_state.selected_person
            if person is None:
                st.session_state.page = "select"
                st.rerun()

            self.show_person(person)

            if person.has_ekg_data() and not st.session_state.get("edit_mode") and not st.session_state.get("add_test_mode"):
                st.subheader("Analyse durchführen")
                test_nr = self.select_test_nr(person)
                self.analysis_manager.run_analysis(person, test_nr)


def main():
    App().main()
