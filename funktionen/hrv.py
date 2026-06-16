#Herzratenvarabilität (HRV) Zusatzaufgabe 

import numpy as np

def calculate_hrv_rmssd(ekg_data):
    """
    Output: HRV (RMSSD) in ms.
    """
    peaks = ekg_data.detect_peaks()  # falls du so eine Funktion hast
    rr = np.diff(peaks)  # RR-Intervalle in ms
    return np.sqrt(np.mean(np.square(np.diff(rr))))
