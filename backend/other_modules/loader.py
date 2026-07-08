from backend.ekg_modules.ekgdata import EKGdata
from backend.ekg_modules.fitdata import FITdata


def load_test(test_dict: dict):
    """Gibt EKGdata oder FITdata zurück, je nach Dateiendung."""

    if test_dict.get("result_link", "").endswith(".fit"):
        return FITdata(test_dict)
    return EKGdata(test_dict)
