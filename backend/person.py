from backend.loader import load_test
import json
from PIL import Image
import datetime 
today = datetime.date.today().year
DB_PATH = "data/persons.json"


class Person:
    """
    Repräsentiert eine Testperson mit Stammdaten, EKG‑Tests
    und grundlegenden Gesundheitsberechnungen.
    """


    def __init__(self, id : int, date_of_birth : int, firstname : str, lastname : str, picture_path : str, ekg_tests : list, gender = "Male"):
        """Initialisiert das Person‑Objekt mit den angegebenen Attributen und EKG‑Tests."""
    
        self.id = id
        self.date_of_birth = date_of_birth
        self.firstname = firstname
        self.lastname = lastname
        self.picture_path = picture_path
        self.ekg_tests = ekg_tests
        self.gender = gender

    @staticmethod
    def load_persons():
        """Lädt alle Personen aus persons.json."""
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return [Person(**p) for p in json.load(f)]
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "date_of_birth": self.date_of_birth,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "picture_path": self.picture_path,
            "ekg_tests": self.ekg_tests,
            "gender": self.gender,
        }

    @staticmethod
    def save_persons(persons: list):
        """Schreibt die Personenliste zurück in persons.json."""
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump([p.to_dict() for p in persons], f, ensure_ascii=False, indent=4)
 
    @staticmethod
    def next_person_id(persons: list) -> int:
        return max((p.id for p in persons), default=0) + 1
 
    @staticmethod
    def next_test_id(persons: list) -> int:
        all_ids = [t["id"] for p in persons for t in p.ekg_tests]
        return max(all_ids, default=100) + 1

    def get_age(self):
        """Output: Alter der Person."""    
        return today - self.date_of_birth

    def calc_max_heart_rate(self):
        """Output: geschätzte maximale Herzfrequenz."""
        age = self.get_age()

        if self.gender == "Male":
            return 220 - age
        else:  # self.gender == "Female"
            return 226 - age

    def get_full_name(self):
        """Output: vollständiger Name der Person."""
        return self.lastname + ", " + self.firstname

    def get_image(self):
        """Output: Bild der Person als PIL‑Image‑Objekt."""
        return Image.open(self.picture_path)
    
    def get_gender(self):
        """Output: Geschlecht der Person."""
        return self.gender

    def has_ekg_data(self):
        """Output: True, wenn die Person EKG‑Daten hat, sonst False."""
        try:
            return self.ekg_tests is not None and len(self.ekg_tests) > 0
        except TypeError:
            return False
        except Exception:
            return False      

    def get_profile_summary (self):
        """Output: Zusammenfassung der Personendaten als Dictionary."""
        return {"Name": self.get_full_name(),
                 "Age": self.get_age(),
                 "Gender": self.get_gender(),
                 "Max Heart Rate": self.calc_max_heart_rate()
                 }  
    def get_first_ekg(self):
        """Output: EKGdata‑Objekt des ersten EKG‑Tests oder None, wenn keine Daten vorhanden."""
        if not self.has_ekg_data():
            return None
        return load_test(self.ekg_tests[0])
    
