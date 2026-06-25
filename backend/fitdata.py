"""
Liest .fit-Dateien (Garmin/Polar/Wahoo) ein.
Abhängigkeiten: pip install fitparse scipypi

Hinweis: .fit-Dateien enthalten BPM-Werte (~1 Hz), keine Rohkurven in mV.
Die BPM-Werte werden normiert, damit dieselbe Schnittstelle wie EKGdata nutzbar ist.
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

try:
    from fitparse import FitFile
except ImportError:
    raise ImportError("Bitte installieren: pip install fitparse")


class FITdata:
    """Herzfrequenz-Zeitreihe aus einer .fit-Datei. Gleiche Schnittstelle wie EKGdata."""

    def __init__(self, fit_dict: dict):
        self.id = fit_dict["id"]
        self.date = fit_dict["date"]
        self._hr_df = self._load_fit(fit_dict["result_link"])
        self.df = self._build_compat_df(self._hr_df)
        self.peaks = []

    @staticmethod
    def _load_fit(path: str) -> pd.DataFrame:
        """Liest BPM + Timestamps aus der .fit-Datei."""
        rows = []
        for record in FitFile(path).get_messages("record"):
            data = {f.name: f.value for f in record}
            if data.get("heart_rate"):
                rows.append({"timestamp": data["timestamp"], "heart_rate": int(data["heart_rate"])})
        if not rows:
            raise ValueError(f"Keine heart_rate-Daten in '{path}'.")
        df = pd.DataFrame(rows)
        t0 = pd.Timestamp(df["timestamp"].iloc[0])
        df["timestamp_ms"] = df["timestamp"].apply(
            lambda t: int((pd.Timestamp(t) - t0).total_seconds() * 1000)
        )
        return df[["timestamp_ms", "heart_rate"]].reset_index(drop=True)

    @staticmethod
    def _build_compat_df(hr_df: pd.DataFrame) -> pd.DataFrame:
        """Baut DataFrame mit Spaltennamen kompatibel zu EKGdata."""
        bpm = hr_df["heart_rate"].astype(float)
        return pd.DataFrame({
            "Zeit in ms": hr_df["timestamp_ms"],
            "Messwerte in mV": (bpm - bpm.mean()) / (bpm.std() + 1e-9) * 100,
            "BPM": bpm,
        })

    def estimate_hr(self) -> float:
        return float(self._hr_df["heart_rate"].mean())

    def find_peaks(self, threshold=0.0, respacing_factor=1):
        from scipy.signal import find_peaks as sp_peaks
        values = self.df["Messwerte in mV"].values
        indices, _ = sp_peaks(values, height=threshold, distance=max(1, respacing_factor))
        self.peaks = list(indices)
        return self.peaks

    def calculate_hrv_rmssd(self):
        bpm = self._hr_df["heart_rate"].values.astype(float)
        if len(bpm) < 3:
            return None
        rr = 60000.0 / bpm
        return float(np.sqrt(np.mean(np.diff(rr) ** 2)))

    def get_duration_minutes(self) -> float:
        ms = self.df["Zeit in ms"]
        return round((ms.iloc[-1] - ms.iloc[0]) / 60000, 2)

    def plot_time_series(self):
        return px.line(self.df, x="Zeit in ms", y="Messwerte in mV",
                       title=f"FIT-Aktivität {self.id}")

    def plot_with_peaks(self):
        if not self.peaks:
            self.find_peaks()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=self.df["Zeit in ms"], y=self.df["Messwerte in mV"],
                                 mode="lines", name="HR", line=dict(color="steelblue")))
        if self.peaks:
            fig.add_trace(go.Scatter(
                x=self.df["Zeit in ms"].iloc[self.peaks],
                y=self.df["Messwerte in mV"].iloc[self.peaks],
                mode="markers", marker=dict(color="red", size=6), name="Peaks"
            ))
        fig.update_layout(title=f"FIT-Aktivität {self.id} mit Peaks",
                          xaxis_title="Zeit in ms", yaxis_title="normierte BPM", height=500)
        return fig

    def plot_with_peaks_window(self, start_min=0, end_min=None):
        if not self.peaks:
            self.find_peaks()
        time_ms_rel = self.df["Zeit in ms"] - self.df["Zeit in ms"].iloc[0]
        time_min = time_ms_rel / 60000
        if end_min is None:
            end_min = float(time_min.iloc[-1])
        mask = (time_min >= start_min) & (time_min <= end_min)
        plot_df = self.df[mask]
        time_sec = time_ms_rel[mask] / 1000

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=time_sec, y=plot_df["Messwerte in mV"],
                                 mode="lines", name="HR", line=dict(color="steelblue")))
        peak_indices = [i for i in self.peaks if i in plot_df.index]
        if peak_indices:
            fig.add_trace(go.Scatter(
                x=time_sec.loc[peak_indices],
                y=plot_df["Messwerte in mV"].loc[peak_indices],
                mode="markers", marker=dict(color="red", size=6), name="Peaks"
            ))
        start_sec = start_min * 60
        tick_vals = [start_sec + i for i in range(5)]
        tick_text = [f"{int(v//60)}m {int(v%60)}s" for v in tick_vals]
        fig.update_layout(
            title=f"FIT-Aktivität {self.id} mit Peaks",
            xaxis=dict(title="Zeit", tickvals=tick_vals, ticktext=tick_text),
            yaxis_title="normierte BPM", height=500
        )
        return fig