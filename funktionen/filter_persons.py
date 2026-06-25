import datetime


def filter_persons(persons, name_filter, gender_filter, age_min, age_max):

    filtered = persons

    # Name
    if name_filter:
        search_terms = [term.strip().lower() for term in name_filter.split() if term.strip()]
        filtered = [
            p for p in filtered
            if any(
                all(term in p.get_full_name().lower() for term in search_terms)
                if len(search_terms) > 1
                else any(term in p.get_full_name().lower() for term in search_terms)
                for _ in [0]
            )
        ]

    # Geschlecht
    if gender_filter != "Alle":
        filtered = [
            p for p in filtered
            if p.gender == gender_filter
        ]

    # Alter
    current_year = datetime.date.today().year

    filtered = [
        p for p in filtered
        if age_min <= (current_year - p.date_of_birth) <= age_max
    ]

    return filtered