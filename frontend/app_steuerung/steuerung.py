import os
import datetime
import streamlit as st

from backend.other_modules.person import Person
from frontend.Login.login import manager

from frontend.app_steuerung import person_manager
from frontend.ekg_plot.analysis_manager import AnalysisManager
from frontend.app_steuerung.navigation import Navigation
from frontend.app_steuerung.session import SessionManager
from frontend.ekg_plot.compare import (
    plot_ekg_overlay,
    get_metric_value,
    get_test_duration_seconds,
    get_window_seconds,
)
from frontend.ekg_plot.utlispatient import get_other_patients, get_comparable_metrics
from frontend.Notizen.notizen import load_notes, save_note, delete_note

# Ensure a light theme and wide layout. `set_page_config` must run before other Streamlit calls.
try:
    st.set_page_config(page_title="Digitale EKG-Datenbank", layout="wide")
except Exception:
    pass

# Fallback CSS to force white background where theme might not cover everything.
st.markdown(
    """
    <style>
    .main .block-container{background-color: #ffffff !important;}
    .stApp {background-color: #ffffff !important;}
    </style>
    """,
    unsafe_allow_html=True,
)


class App:
    '''Hauptklasse der Streamlit-App, die die Navigation und Anzeige von Seiten basierend auf Benutzerinteraktionen verwaltet.'''

    def __init__(self):
        '''Initialisiert die App und ihre Manager.'''
        self.person_manager = person_manager.PersonManager()
        self.analysis_manager = AnalysisManager()

    def home(self):
        '''Rendert die Startseite der App mit Optionen basierend auf der Rolle des Benutzers.'''
        st.title("Digitale EKG-Datenbank 🫀")

        display_name = st.session_state.username
        if st.session_state.role == "patient":
            patient = st.session_state.get("selected_person")
            if patient is None and st.session_state.get("person_id") is not None:
                patient = next(
                    (p for p in self.person_manager.persons if p.id == st.session_state.person_id),
                    None,
                )
            if patient is not None:
                display_name = f"{patient.firstname} {patient.lastname}"

        st.subheader(f"Herzlich Willkommen, {display_name}!")

        if st.session_state.role != "patient":
            st.write("Was möchten Sie tun?")

            col2, col1 = st.columns(2)

            with col1:
                if st.button(
                    "➕ Neuen Patienten hinzufügen",
                    key="home_add_patient",
                    width = "stretch",
                    type="secondary"
                ):
                    st.session_state.page = "add_person_form"
                    st.rerun()

            with col2:
                if st.button(
                    "🔍 Patienten suchen",
                    key="home_search_patient",
                    width = "stretch",
                    type="primary"
                ):
                    st.session_state.page = "select"
                    st.rerun()

            col3, col4 = st.columns(2)

            with col4:
                if st.button(
                    "🚪 Logout",
                    key="home_logout",
                    width = "stretch",
                    type="secondary"
                ):
                    manager.logout(force=True)

            with col3:
                if st.button(
                    "📝 Notizen",
                    key="home_notes",
                    width = "stretch",
                    type="secondary",
                ):
                    st.session_state.page = "notes"
                    st.rerun()

        else:
            st.info(
                "Hier können Sie Ihre eigenen EKG-Daten und Analysen einsehen. "
                "Neue Tests oder Änderungen können ausschließlich vom medizinischen Personal vorgenommen werden."
            )

            col1, col2 = st.columns(2)

            with col1:
                if st.button(
                    "🫀 Meine EKG-Daten anzeigen",
                    key="home_patient_data",
                    width = "stretch",
                    type="primary"
                ):
                    patient_id = st.session_state.get("person_id")
                    if patient_id is not None:
                        patient = next(
                            (p for p in self.person_manager.persons if p.id == patient_id),
                            None,
                        )
                        if patient is not None:
                            st.session_state.selected_person = patient
                            st.session_state.page = "analysis"
                            st.rerun()
                        else:
                            st.error("Zu diesem Benutzerkonto konnte kein Patient gefunden werden.")
                    else:
                        st.error("Ihr Benutzerkonto ist nicht korrekt verknüpft.")

            with col2:
                if st.button(
                    "🚪 Logout",
                    key="home_patient_logout",
                    width = "stretch",
                    type="secondary"
                ):
                    manager.logout(force=True)

    def show_notes(self):
        st.button("⬅ Zurück", key="notes_back", on_click=Navigation.go_home)
        st.header("Notizen")
        st.write("Hier ist Platz für persönliche Notizen und Anmerkungen. Nur Sie haben Zugriff auf diese Notizen.")
        notes = load_notes()  

        if notes:
            st.subheader("Vorhandene Notizen")
            for i, n in enumerate(notes):
                col_text, col_action = st.columns([9, 1])
                with col_text:
                    st.write(f"{n.get('datum')} — {n.get('text')}")
                with col_action:
                    if st.button("Löschen", key=f"delete_note_{i}"):
                        ok = delete_note(i)
                        if ok:
                            st.success("Notiz gelöscht.")
                            st.rerun()
                        else:
                            st.error("Löschen fehlgeschlagen.")
        else:
            st.info("Keine Notizen vorhanden.")

        st.subheader("Neue Notiz hinzufügen")
        new = st.text_area("Neue Notiz", key="new_note_text")
        if st.button("Speichern", key="save_new_note"):
            if not new.strip():
                st.error("Notiz ist leer.")
            else:
                save_note(new.strip())
                st.success("Notiz gespeichert.")
                st.rerun()






    # --- Person auswählen ---

    def select_person(self):
        '''Rendert die Seite zur Patientenauswahl mit Filteroptionen und ermöglicht das Hinzufügen neuer Patienten.'''

        st.header("Filter")

        st.button("⬅ Zurück", key="select_back", on_click=Navigation.go_home)

        name_filter = st.text_input("Suche nach Vor- oder Nachname")
        filtered = self.person_manager.get_filtered(name_filter)

        if not filtered:
            st.warning("Keine passenden Patienten gefunden.")
        
        else:
            st.subheader("Patientenliste")
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
                    if st.button("Patient:in löschen 🗑️", key="select_delete"):
                        self.person_manager.delete_person(selected_person)

        #if st.session_state.get("role") != "patient":
            #with st.expander("➕ Neue Person hinzufügen"):
                #self.add_person_form()

    # --- Neue Person hinzufügen ---

    def add_person_form(self):
        '''Rendert das Formular zum Hinzufügen einer neuen Person mit Eingabefeldern für Name, Geburtsjahr, Geschlecht und optionales Bild.'''

        st.subheader("➕ Neue Patienten hinzufügen")
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

            username, password = manager.create_patient_account(new_person)
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
        '''Rendert die Detailansicht einer ausgewählten Person mit Tabs für allgemeine Informationen, EKG-Analysen und Vergleichsmöglichkeiten.'''

        
        st.header(person.get_full_name())
        st.button("⬅ Zurück zur Startseite", key="show_person_back", on_click=Navigation.go_home)

        #st.markdown(unsafe_allow_html=True)

        tab_info, tab_tests, tab_comparison = st.tabs(["🛈 Allgemeine Informationen", "📊 Auswertungen", "↔ Vergleich"])

        with tab_info:
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


            # Editier- und Test-Hinzufügen-Bereich nur für berechtigte Rollen
            if st.session_state.get("role") != "patient":
                with st.expander("✏️ Person editieren"):
                    self.edit_person_form(person)

                with st.expander("➕ Test hinzufügen"):
                    self.add_test_form(person)
            else:
                st.info("Sie haben keine Berechtigung, Daten zu bearbeiten oder neue Tests hinzuzufügen.")

        with tab_tests:
            st.subheader("EKG & HRV Auswertungen")

            if not person.ekg_tests:
                st.info("Keine EKG-Daten vorhanden.")
            else:
                # Test-Auswahl
                labels = [f"Test {i+1}" for i in range(len(person.ekg_tests))]
                selected = st.selectbox("Bitte Test auswählen:", labels, key="test_select_show_person")
                idx = labels.index(selected)
                test = person.ekg_tests[idx]

                if st.session_state.get("role") != "patient":
                    if st.button("Löschen", key="delete_selected_test"):
                        del person.ekg_tests[idx]
                        Person.save_persons(self.person_manager.persons)
                        st.success(f"Test {test['id']} wurde gelöscht.")
                        st.rerun()

                st.write(f"**Test-ID:** {test['id']}")
                st.write(f"**Datum:** {test.get('date', 'unbekannt')}")

                # Beispiel: EKG-Daten anzeigen
                if "ekg" in test:
                    st.line_chart(test["ekg"])

                # Beispiel: HRV-Daten anzeigen
                if "hrv" in test:
                    st.line_chart(test["hrv"])

                self.analysis_manager.run_analysis(person, idx, persons=self.person_manager.persons)

        with tab_comparison:
            st.subheader("↔ Vergleich von EKG-Daten")

            self.person_manager.persons = Person.load_persons()
            person = next((p for p in self.person_manager.persons if p.id == person.id), person)

            if st.session_state.role in ["admin", "doctor"]:
                if len(person.ekg_tests) >= 2:
                    same_patient_compare = st.checkbox(
                        "Mit zweitem Test desselben Patienten vergleichen",
                        key="admin_same_patient_compare",
                    )
                else:
                    same_patient_compare = False

                if same_patient_compare:
                    st.markdown("**Vergleich desselben Patienten**")
                    test_options_a = [f"Test {t['id']} ({t.get('date', 'ohne Datum')})" for t in person.ekg_tests]
                    selected_test_a = st.selectbox(
                        "Erster Test",
                        test_options_a,
                        key="compare_test_a",
                    )
                    selected_test_b = st.selectbox(
                        "Zweiter Test",
                        test_options_a,
                        key="compare_test_b",
                    )
                    other_person = person
                else:
                    other_patients = get_other_patients(person, self.person_manager.persons)
                    if not other_patients:
                        st.info("Es sind keine weiteren Patienten vorhanden, mit denen verglichen werden kann.")
                        other_person = None
                    else:
                        col_left, col_right = st.columns([2, 2])

                        with col_left:
                            st.markdown("**Patient A**")
                            st.write(person.get_full_name())
                            test_options_a = [f"Test {t['id']} ({t.get('date', 'ohne Datum')})" for t in person.ekg_tests]
                            selected_test_a = st.selectbox(
                                "Test auswählen",
                                test_options_a if test_options_a else ["Keine Tests verfügbar"],
                                key="compare_test_a",
                            )

                        with col_right:
                            st.markdown("**Patient B**")
                            names = [p.get_full_name() for p in other_patients]
                            selected_name = st.selectbox(
                                "Bitte zweiten Patienten auswählen:",
                                names,
                                key="compare_other_patient",
                            )
                            other_person = next(p for p in other_patients if p.get_full_name() == selected_name)
                            test_options_b = [f"Test {t['id']} ({t.get('date', 'ohne Datum')})" for t in other_person.ekg_tests]
                            selected_test_b = st.selectbox(
                                "Test auswählen",
                                test_options_b if test_options_b else ["Keine Tests verfügbar"],
                                key="compare_test_b",
                            )

                if other_person is not None and person.ekg_tests and other_person.ekg_tests:
                    if selected_test_a == "Keine Tests verfügbar" or selected_test_b == "Keine Tests verfügbar":
                        st.info("Für einen der beiden ausgewählten Tests sind noch keine Daten vorhanden.")
                    elif same_patient_compare and selected_test_a == selected_test_b:
                        st.warning("Bitte wählen Sie zwei unterschiedliche Tests desselben Patienten aus.")
                    else:
                        selected_metrics = st.session_state.get("compare_metrics", get_comparable_metrics())

                        duration_a = get_test_duration_seconds(person, selected_test_a)
                        duration_b = get_test_duration_seconds(other_person, selected_test_b)
                        common_duration = min(duration_a, duration_b)
                        window_sec = min(get_window_seconds(person, selected_test_a), get_window_seconds(other_person, selected_test_b))
                        max_start = max(0, int(round(common_duration - window_sec)))
                        start_sec = 0
                        if max_start > 0:
                            start_sec = st.slider(
                                "Zeitbereich",
                                0,
                                max_start,
                                0,
                                key="compare_time_slider",
                            )
                        st.caption(f"Position: {start_sec // 60}m {start_sec % 60}s")

                        try:
                            fig, norm_stats = plot_ekg_overlay(
                                person,
                                other_person,
                                selected_test_a=selected_test_a,
                                selected_test_b=selected_test_b,
                                start_sec=start_sec,
                                window_sec=window_sec,
                                label_a="Test A",
                                label_b="Test B",
                            )
                            config = {
                                "scrollZoom": False,
                                "modeBarButtonsToRemove": ["select2d", "lasso2d", "zoom2d", "autoScale2d", "resetScale2d"],
                                "displaylogo": False,
                            }
                            st.plotly_chart(fig, width='stretch', config=config)

                            selected_metrics = get_comparable_metrics()
                            metrics_a = {metric: get_metric_value(person, selected_test_a, metric) for metric in selected_metrics}
                            metrics_b = {metric: get_metric_value(other_person, selected_test_b, metric) for metric in selected_metrics}

                            if selected_metrics:
                                st.markdown("**Vergleichswerte**")
                                rows = []
                                for metric in selected_metrics:
                                    rows.append({
                                        "Metrik": metric,
                                        "Test A": f"<span style=\"color:#2563eb;font-weight:bold;\">{metrics_a[metric]}</span>",
                                        "Test B": f"<span style=\"color:#dc2626;font-weight:bold;\">{metrics_b[metric]}</span>",
                                    })

                                html = "<table style='width:100%;border-collapse:collapse;'>"
                                html += "<thead><tr><th style='text-align:left;padding:8px;border-bottom:1px solid #ddd;'>Metrik</th><th style='text-align:left;padding:8px;border-bottom:1px solid #ddd;'>Test A</th><th style='text-align:left;padding:8px;border-bottom:1px solid #ddd;'>Test B</th></tr></thead><tbody>"
                                for row in rows:
                                    html += f"<tr><td style='padding:8px;border-bottom:1px solid #eee;'>{row['Metrik']}</td><td style='padding:8px;border-bottom:1px solid #eee;'>{row['Test A']}</td><td style='padding:8px;border-bottom:1px solid #eee;'>{row['Test B']}</td></tr>"
                                html += "</tbody></table>"
                                st.markdown(html, unsafe_allow_html=True)

                        except Exception as exc:
                            st.error(f"Der Vergleich konnte nicht erstellt werden: {exc}")
                else:
                    if not same_patient_compare:
                        st.info("Für mindestens einen der beiden Patienten liegen noch keine EKG-Daten vor.")

            else:
                st.markdown("**Eigener Testvergleich für Patienten**")
                test_options = [f"Test {t['id']} ({t.get('date', 'ohne Datum')})" for t in person.ekg_tests]

                if len(test_options) < 2:
                    st.info("Mindestens zwei eigene Tests werden benötigt, um einen Vergleich durchzuführen.")
                else:
                    col_a, col_b = st.columns(2)
                    with col_a:
                        selected_test_a = st.selectbox(
                            "Erster eigener Test",
                            test_options,
                            key="patient_compare_test_a",
                        )
                    with col_b:
                        selected_test_b = st.selectbox(
                            "Zweiter eigener Test",
                            test_options,
                            key="patient_compare_test_b",
                        )

                    if selected_test_a == selected_test_b:
                        st.warning("Bitte wählen Sie zwei unterschiedliche Tests für den Vergleich aus.")
                    else:
                        duration_a = get_test_duration_seconds(person, selected_test_a)
                        duration_b = get_test_duration_seconds(person, selected_test_b)
                        common_duration = min(duration_a, duration_b)
                        window_sec = min(get_window_seconds(person, selected_test_a), get_window_seconds(person, selected_test_b))
                        max_start = max(0, int(round(common_duration - window_sec)))
                        start_sec = 0
                        if max_start > 0:
                            start_sec = st.slider(
                                "Zeitbereich",
                                0,
                                max_start,
                                0,
                                key="compare_norm_time_slider",
                            )
                        st.caption(f"Position: {start_sec // 60}m {start_sec % 60}s")
                        try:
                            fig, _ = plot_ekg_overlay(
                                person,
                                person,
                                selected_test_a=selected_test_a,
                                selected_test_b=selected_test_b,
                                start_sec=start_sec,
                                window_sec=window_sec,
                                label_a="Test A",
                                label_b="Test B",
                                title="Vergleich der 2 Tests",
                            )
                            config = {
                                "scrollZoom": False,
                                "modeBarButtonsToRemove": ["select2d", "lasso2d", "zoom2d", "autoScale2d", "resetScale2d"],
                                "displaylogo": False,
                            }
                            st.plotly_chart(fig, width="stretch", config=config)
                        except Exception as exc:
                            st.error(f"Der Vergleich konnte nicht erstellt werden: {exc}")

    def _go_home(self):
        '''Setzt die App-Navigation auf die Startseite zurück.'''

        st.session_state.page = "home"

    def _show_add_person_form(self):
        '''Setzt die App-Navigation auf das Formular zum Hinzufügen einer neuen Person zurück.'''

        st.session_state.page = "add_person_form"

    # --- Person editieren ---

    def edit_person_form(self, person):
        '''Rendert das Formular zum Editieren der Informationen einer Person mit Eingabefeldern für Name, Geburtsjahr, Geschlecht und optionales Bild.'''

        st.subheader("✏️ Patient:in bearbeiten")
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
        '''Rendert das Formular zum Hinzufügen eines neuen EKG-Tests für eine Person mit Eingabefeldern für Datum und Datei-Upload.'''
        
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

        if not manager.login():
            st.stop()
        manager.logout()

        col1, col2 = st.columns([2, 1])
        with col2:
            st.image("data/images/Logo_EKGApp.png", width=300)


        st.sidebar.write(f"Angemeldet als: {st.session_state.username}")

        page = st.session_state.page

        if page == "home":
            self.home()
        elif page == "select":
            self.select_person()
        elif page == "add_person_form":
            self.add_person_form()
        elif page == "notes":
            self.show_notes()
        elif page == "analysis":
            person = st.session_state.selected_person
            if person is None and st.session_state.get("role") == "patient":
                patient_id = st.session_state.get("person_id")
                if patient_id is not None:
                    person = next(
                        (p for p in self.person_manager.persons if p.id == patient_id),
                        None,
                    )
                    st.session_state.selected_person = person
            if person is None:
                st.session_state.page = "select"
                st.rerun()

            self.show_person(person)

def main():
    '''Startet die App.'''
    
    App().main()
