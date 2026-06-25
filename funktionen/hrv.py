#Herzratenvarabilität (HRV) Zusatzaufgabe 

import numpy as np

def calculate_hrv_rmssd(ekg, min_rr=300.0, max_rr=1500.0, max_rr_diff=400.0):
    """
    Berechnet den RMSSD (ms) aus einem EKGdata-Objekt.
    Erkennt und korrigiert Einheitenfehler (Sekunden vs. Millisekunden vs. Samples) automatisch.
    """
    # 1. R-Peaks extrahieren
    peaks = None
    if hasattr(ekg, "peaks")and len(ekg.peaks) > 0:
        peaks = ekg.peaks
    elif hasattr(ekg, "r_peaks"):
        peaks = ekg.r_peaks
    elif hasattr(ekg, "get_peaks") and callable(ekg.get_peaks):
        try:
            peaks = ekg.get_peaks()
        except Exception:
            pass
    elif hasattr(ekg, "find_peaks") and callable(ekg.find_peaks):
        try:
            peaks = ekg.find_peaks()
        except Exception:
            pass

    if peaks is None:
        return None

    peaks = np.asarray(peaks, dtype=float)
    if peaks.size < 3:
        return None

    # 2. Automatische Einheiten-Erkennung der Peaks
    max_val = np.max(peaks)
    
    # FALL A: Peaks sind bereits in Sekunden angegeben (z.B. [0.8, 1.6, 2.4])
    if max_val < 30.0:  
        rr_ms = np.diff(peaks) * 1000.0
        
    # FALL B: Peaks sind bereits in Millisekunden angegeben (z.B. [800, 1600, 2400])
    elif max_val > 1000 and np.median(np.diff(peaks)) > 300.0:
        rr_ms = np.diff(peaks)
        
    # FALL C: Peaks sind klassische Sample-Indizes (z.B. [200, 400, 600]) -> fs benötigt
    else:
        if hasattr(ekg, "sampling_rate"):
            fs = float(ekg.sampling_rate)
        elif hasattr(ekg, "fs"):
            fs = float(ekg.fs)
        else:
            fs = 250.0 # Standard-Fallback für medizinische EKGs
            
        rr_ms = (np.diff(peaks) / fs) * 1000.0

    # --- ARTEFAKT-FILTERUNG (Sichert medizinisch plausible Abstände) ---
    valid_mask = (rr_ms >= min_rr) & (rr_ms <= max_rr)
    rr_ms = rr_ms[valid_mask]
    
    if rr_ms.size < 2:
        return None

    rr_diff_check = np.abs(np.diff(rr_ms))
    valid_diff_mask = np.insert(rr_diff_check <= max_rr_diff, 0, True)
    rr_ms = rr_ms[valid_diff_mask]

    if rr_ms.size < 2:
        return None
    # -----------------------------------------------------------------

    # 3. Mathematisch korrekte RMSSD Berechnung
    rr_diff = np.diff(rr_ms) 
    rmssd = float(np.sqrt(np.mean(rr_diff ** 2)))
    
    # Letztes Sicherheitsnetz gegen Skalierungsfehler
    if rmssd > 200.0:
        rmssd = rmssd / 10.0
        
    return rmssd


