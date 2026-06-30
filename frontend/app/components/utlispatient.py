def get_other_patients(current, all_patients):
    return [p for p in all_patients if p.id != current.id]

def get_comparable_metrics():
    return [
        "EKG",
        "HR_max",
        "HRV RMSSD",
        "Durchschnittspuls"
    ]
