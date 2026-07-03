def filter_persons(persons, name_filter):
    '''Filtert die Personenliste basierend auf dem angegebenen Namen.'''

    filtered = persons

    if name_filter:
        search_terms = [term.strip().lower() for term in name_filter.split() if term.strip()]
        filtered = [
            p for p in filtered
            if all(term in p.get_full_name().lower() for term in search_terms)
        ]
    return filtered