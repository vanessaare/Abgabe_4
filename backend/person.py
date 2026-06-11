import json
from PIL import Image
import datetime 
today = datetime.date.today().year

class Person:

    def __init__(self, id : int, date_of_birth : int, firstname : str, lastname : str, picture_path : str, ekg_tests : list, gender = "Male"):
        self.id = id
        self.date_of_birth = date_of_birth
        self.firstname = firstname
        self.lastname = lastname
        self.picture_path = picture_path
        self.ekg_tests = ekg_tests
        self.gender = gender

    @staticmethod   
    def load_persons():
        with open("data/persons.json", "r", encoding="utf-8") as file:
            person_data = json.load(file)

        persons = []

        for person_dict in person_data:
            person = Person(
                person_dict["id"],
                person_dict["date_of_birth"],
                person_dict["firstname"],
                person_dict["lastname"],
                person_dict["picture_path"],
                person_dict["ekg_tests"],
                person_dict["gender"]
            )
            persons.append(person)

        return persons




    def get_age(self):        
        return today - self.date_of_birth

    def calc_max_heart_rate(self):
        age = self.get_age()

        if self.gender == "Male":
            return 220 - age
        else:  # self.gender == "Female"
            return 226 - age

    def get_full_name(self):
        return self.lastname + ", " + self.firstname

    def get_image(self):
        return Image.open(self.picture_path)
    
    def get_gender(self):
        return self.gender

    def has_ekg_data(self):
        try:
            return self.ekg_tests is not None and len(self.ekg_tests) > 0
        except TypeError:
            return False
        except Exception:
            return False      

    def get_profile_summary (self):
        return {"Name": self.get_full_name(),
                 "Age": self.get_age(),
                 "Gender": self.get_gender(),
                 "Max Heart Rate": self.calc_max_heart_rate()
                 }  

    