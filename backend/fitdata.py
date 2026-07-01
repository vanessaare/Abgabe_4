"""
Liest .fit-Dateien ein und erzeugt daraus ein synthetisches EKG-Signal.
BPM-Werte werden via RR-Intervalle in eine PQRST-Kurve bei 250 Hz umgewandelt,
sodass dieselbe Schnittstelle wie EKGdata nutzbar ist.

Abhängigkeiten: pip install fitparse scipy
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.signal import find_peaks as sp_find_peaks

try:
    from fitparse import FitFile
except ImportError:
    raise ImportError("Bitte installieren: pip install fitparse")

FS = 250  # synthetische Abtastrate in Hz


class FITdata:
    """Synthetisches EKG aus .fit-Datei. Gleiche Schnittstelle wie EKGdata."""

    def __init__(self, fit_dict: dict):
        self.id = fit_dict["id"]
        self.date = fit_dict["date"]
        self._hr_df = self._load_fit(fit_dict["result_link"])
        self.df = self._build_ecg_df(self._hr_df)
        self.peaks = []

    # ------------------------------------------------------------------

    @staticmethod
    def _load_fit(path: str) -> pd.DataFrame:
        """Liest BPM + Timestamps aus der .fit-Datei."""
        rows = []
        for record in FitFile(path).get_messages("record"):
            data = {f.name: f.value for f in record}
            if data.get("heart_rate"):
                rows.append({"timestamp": data["timestamp"],
                              "heart_rate": int(data["heart_rate"])})
        if not rows:
            raise ValueError(f"Keine heart_rate-Daten in '{path}'.")
        df = pd.DataFrame(rows)
        t0 = pd.Timestamp(df["timestamp"].iloc[0])
        df["timestamp_ms"] = df["timestamp"].apply(
            lambda t: int((pd.Timestamp(t) - t0).total_seconds() * 1000)
        )
        return df[["timestamp_ms", "heart_rate"]].reset_index(drop=True)

    @staticmethod
    def _pqrst_template() -> np.ndarray:
        """Ein synthetischer PQRST-Herzschlag (1 Sekunde bei FS Hz)."""
        t = np.linspace(0, 1, FS, endpoint=False)
        ecg = np.zeros(FS)
        ecg += 0.15 * np.exp(-((t - 0.15) ** 2) / (2 * 0.012 ** 2))   # P
        ecg -= 0.10 * np.exp(-((t - 0.22) ** 2) / (2 * 0.004 ** 2))   # Q
        ecg += 1.00 * np.exp(-((t - 0.25) ** 2) / (2 * 0.005 ** 2))   # R
        ecg -= 0.15 * np.exp(-((t - 0.28) ** 2) / (2 * 0.004 ** 2))   # S
        ecg += 0.25 * np.exp(-((t - 0.40) ** 2) / (2 * 0.025 ** 2))   # T
        return ecg

    @staticmethod
    def _build_ecg_df(hr_df: pd.DataFrame) -> pd.DataFrame:
        """Erzeugt synthetisches EKG-Signal aus BPM-Zeitreihe."""
        bpm = hr_df["heart_rate"].values.astype(float)
        ts  = hr_df["timestamp_ms"].values.astype(float)

        total_ms      = ts[-1] - ts[0]
        total_samples = int(total_ms / 1000 * FS)
        time_axis_ms  = np.linspace(0, total_ms, total_samples)

        # BPM auf 250 Hz interpolieren → RR in Samples
        bpm_interp = np.interp(time_axis_ms, ts - ts[0], bpm)
        rr_samples = (60.0 / bpm_interp * FS).astype(int)

        template = FITdata._pqrst_template()  # statisch aufrufen
        ecg      = np.zeros(total_samples)
        pos      = 0
        while pos < total_samples:
            end   = min(pos + len(template), total_samples)
            ecg[pos:end] += template[:end - pos]
            pos  += max(1, int(rr_samples[min(pos, total_samples - 1)]))

        return pd.DataFrame({
            "Zeit in ms":     time_axis_ms,
            "Messwerte in mV": ecg,
        })

    def estimate_hr(self) -> float:
        hr = self._hr_df["heart_rate"]

        # Realistische Werte filtern
        hr_filtered = hr[(hr > 35) & (hr < 210)]

        if len(hr_filtered) == 0:
            return float("nan")   # oder 0, je nach App-Logik

        return float(hr_filtered.mean())

    def find_peaks(self, threshold=350, respacing_factor=5):
        """Peaks im synthetischen EKG (R-Zacken)."""
        values   = self.df["Messwerte in mV"].values
        distance = max(1, int(FS * 0.4))  # mind. 0.4 s zwischen Peaks
        indices, _ = sp_find_peaks(values, height=0.5, distance=distance)
        self.peaks = list(indices)
        return self.peaks

    def calculate_hrv_rmssd(self):
        if not self.peaks:
            self.find_peaks()
        if len(self.peaks) < 3:
            return None
        peak_times = self.df["Zeit in ms"].iloc[self.peaks].values
        rr   = np.diff(peak_times)
        return float(np.sqrt(np.mean(np.diff(rr) ** 2)))

    def get_duration_minutes(self) -> float:
        ms = self.df["Zeit in ms"]
        return round((ms.iloc[-1] - ms.iloc[0]) / 60000, 2)

    # ------------------------------------------------------------------

    def plot_time_series(self):
        return px.line(self.df, x="Zeit in ms", y="Messwerte in mV",
                       title=f"FIT-Aktivität {self.id} – synthetisches EKG")

    def plot_with_peaks(self):
        if not self.peaks:
            self.find_peaks()
        plot_df = self.df.head(2000)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=plot_df["Zeit in ms"], y=plot_df["Messwerte in mV"],
                                 mode="lines", name="EKG (synth.)", line=dict(color="steelblue")))
        peak_idx = [i for i in self.peaks if i in plot_df.index]
        if peak_idx:
            fig.add_trace(go.Scatter(
                x=plot_df["Zeit in ms"].loc[peak_idx],
                y=plot_df["Messwerte in mV"].loc[peak_idx],
                mode="markers", marker=dict(color="red", size=6), name="Peaks"
            ))
        fig.update_layout(title=f"FIT-Aktivität {self.id} mit Peaks",
                          xaxis_title="Zeit in ms", yaxis_title="mV", height=500)
        return fig

    def plot_with_peaks_window(self, start_min=0, end_min=None):
        if not self.peaks:
            self.find_peaks()
        time_ms_rel = self.df["Zeit in ms"] - self.df["Zeit in ms"].iloc[0]
        time_min    = time_ms_rel / 60000
        if end_min is None:
            end_min = float(time_min.iloc[-1])
        mask    = (time_min >= start_min) & (time_min <= end_min)
        plot_df = self.df[mask]
        time_sec = time_ms_rel[mask] / 1000

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=time_sec, y=plot_df["Messwerte in mV"],
                                 mode="lines", name="EKG (synth.)", line=dict(color="steelblue")))
        peak_idx = [i for i in self.peaks if i in plot_df.index]
        if peak_idx:
            fig.add_trace(go.Scatter(
                x=time_sec.loc[peak_idx],
                y=plot_df["Messwerte in mV"].loc[peak_idx],
                mode="markers", marker=dict(color="red", size=6), name="Peaks"
            ))
        start_sec = start_min * 60
        tick_vals = [start_sec + i for i in range(5)]
        tick_text = [f"{int(v//60)}m {int(v%60)}s" for v in tick_vals]
        fig.update_layout(
            title=f"FIT-Aktivität {self.id} mit Peaks (synthetisches EKG)",
            xaxis=dict(title="Zeit", tickvals=tick_vals, ticktext=tick_text),
            yaxis_title="mV", height=500
        )
        return fig