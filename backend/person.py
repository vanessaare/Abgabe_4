from backend.loader import load_test
from PIL import Image
import json
import os
import datetime
from tinydb import TinyDB

today  = datetime.date.today().year
DB_PATH = "data/persons.db.json"


class Person:
    """Testperson mit Stammdaten und EKG-Tests. Persistenz via TinyDB."""

    def __init__(self, id, date_of_birth, firstname, lastname, picture_path, ekg_tests, gender="Male"):
        self.id            = id
        self.date_of_birth = date_of_birth
        self.firstname     = firstname
        self.lastname      = lastname
        self.picture_path  = picture_path
        self.ekg_tests     = ekg_tests
        self.gender        = gender

    # ------------------------------------------------------------------
    # DB-Hilfsfunktion
    # ------------------------------------------------------------------

    @staticmethod
    def _db() -> TinyDB:
        return TinyDB(DB_PATH, ensure_ascii=False, indent=4)

    # ------------------------------------------------------------------
    # Laden / Speichern
    # ------------------------------------------------------------------

    @staticmethod
    def load_persons() -> list:
        """Lädt alle Personen aus TinyDB."""
        with Person._db() as db:
            return [Person(**row) for row in db.all()]

    @staticmethod
    def save_persons(persons: list):
        """Überschreibt die komplette DB mit der aktuellen Personenliste."""
        with Person._db() as db:
            db.truncate()
            db.insert_multiple(p.to_dict() for p in persons)

    @staticmethod
    def next_person_id(persons: list) -> int:
        return max((p.id for p in persons), default=0) + 1

    @staticmethod
    def next_test_id(persons: list) -> int:
        all_ids = [t["id"] for p in persons for t in p.ekg_tests]
        return max(all_ids, default=100) + 1

    # ------------------------------------------------------------------
    # Migration: persons.json → TinyDB (einmalig)
    # ------------------------------------------------------------------

    @staticmethod
    def migrate_from_json(json_path: str = "data/persons.json"):
        """Liest die alte persons.json ein und schreibt sie in TinyDB.""" 
        if not os.path.exists(json_path):
            return
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        with Person._db() as db:
            if len(db) == 0:          # nur wenn DB noch leer ist
                db.insert_multiple(data)
                print(f"Migration: {len(data)} Personen übernommen.")

    # ------------------------------------------------------------------
    # Serialisierung
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "id":            self.id,
            "date_of_birth": self.date_of_birth,
            "firstname":     self.firstname,
            "lastname":      self.lastname,
            "picture_path":  self.picture_path,
            "ekg_tests":     self.ekg_tests,
            "gender":        self.gender,
        }

    # ------------------------------------------------------------------
    # Berechnungen & Hilfsmethoden
    # ------------------------------------------------------------------

    def get_full_name(self):
        return f"{self.lastname}, {self.firstname}"

    def get_age(self):
        return today - self.date_of_birth

    def calc_max_heart_rate(self):
        return (220 if self.gender == "Male" else 226) - self.get_age()

    def get_image(self):
        return Image.open(self.picture_path)

    def get_gender(self):
        return self.gender

    def has_ekg_data(self):
        try:
            return bool(self.ekg_tests)
        except Exception:
            return False

    def get_profile_summary(self):
        return {
            "Name": self.get_full_name(),
            "Age": self.get_age(),
            "Gender": self.get_gender(),
            "Max Heart Rate": self.calc_max_heart_rate(),
        }

    def get_first_ekg(self):
        return load_test(self.ekg_tests[0]) if self.has_ekg_data() else None