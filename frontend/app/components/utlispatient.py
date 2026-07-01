
# --- Patientenvergleichs- und Metrik-Hilfsfunktionen ---

def get_other_patients(current, all_patients):
    '''Gibt eine Liste aller Patienten zurück, die nicht der aktuelle Patient sind.'''

    return [p for p in all_patients if p.id != current.id]

def get_comparable_metrics():
    '''Gibt eine Liste der Metriken zurück, die für den Vergleich zwischen Patienten verfügbar sind.'''

    return [
        "EKG",
        "HR_max",
        "HRV RMSSD",
        "Durchschnittspuls"
    ]
