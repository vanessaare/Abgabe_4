import numpy as np
from scipy.signal import find_peaks

# --- EKG Signalverarbeitung und Analyse ---

def smooth_ecg(df, window=5):
    '''Glättet das EKG-Signal mit einem Rolling-Window.'''

    df = df.copy()
    df["voltage_smooth"] = df["voltage"].rolling(window, center=True).mean()
    return df


def detect_r_peaks(df, height=None, distance=None):
    '''Findet R-Peaks im EKG-Signal.'''

    peaks, _ = find_peaks(df["voltage"], height=height, distance=distance)
    return peaks


def compute_rr_intervals(peaks, sampling_rate):
    '''Berechnet die RR-Intervalle aus den R-Peaks.'''

    rr = np.diff(peaks) / sampling_rate * 1000  # in ms
    return rr


def compute_rmssd(rr_intervals):
    '''Berechnet den RMSSD-Wert aus den RR-Intervallen.'''
    
    if len(rr_intervals) < 2:
        return None
    diff_rr = np.diff(rr_intervals)
    return np.sqrt(np.mean(diff_rr**2))


def normalize_ecg(df):
    '''Normalisiert das EKG-Signal (z-Score).'''

    df = df.copy()
    df["voltage_norm"] = (df["voltage"] - df["voltage"].mean()) / df["voltage"].std()
    return df


def resample_ecg(df, target_rate):
    '''Resampled das EKG-Signal auf eine Zielrate (Hz).'''

    df_resampled = df.set_index("time").resample(f"{1000/target_rate}ms").mean().interpolate()
    df_resampled.reset_index(inplace=True)
    return df_resampled
