import pandas as pd
import plotly.express as px
import numpy as np
from funktionen.peak_detection import peak_detection
import plotly.graph_objects as go


class EKGdata:
    """
    Klasse zur Verwaltung, Analyse und Visualisierung von EKG‑Messdaten.
    Lädt die Rohdaten, speichert sie als DataFrame und bietet Funktionen
    zur Peak‑Erkennung, Herzfrequenzschätzung und Plot‑Darstellung.
    """

    def __init__(self, ekg_dict):
        """
     Initialisiert das Objekt mit einem EKG‑Datensatz.
     Lädt die Daten aus der angegebenen Datei und speichert sie als DataFrame.
     """
        
        #pass
        self.id = ekg_dict["id"]
        self.date = ekg_dict["date"]
        self.data = ekg_dict["result_link"]
        self.df = pd.read_csv(self.data, sep='\t', header=None, names=['Messwerte in mV','Zeit in ms',])
        #self.df = self.df.iloc[:5000]  

    @staticmethod
    def load_by_id(test_id: int, person_database: list):
        """
    Input: Test‑ID und Personendatenbank.
    Output: EKGdata‑Objekt oder None.
    """
        for person in person_database:
            for test in person.get("ekg_tests", []):
                if test["id"] == test_id:
                    return EKGdata(test) 
        return None

    def plot_time_series(self):
        """
    Input: keine (eingelesener DataFrame).
    Output: Liniendiagramm des EKG‑Signals.
    """
        plot_df = self.df.head(2000)
        self.fig = px.line(
            plot_df,
            x="Zeit in ms",
            y="Messwerte in mV",
            title=f"EKG Signal {self.id}"
        )
        if not plot_df.empty:
            self.fig.update_xaxes(
                range=[plot_df["Zeit in ms"].iloc[0], plot_df["Zeit in ms"].iloc[-1]]
            )
        return self.fig

    def find_peaks(self, threshold=350, respacing_factor=5):
        """ Input: Schwellenwert und Resampling‑Faktor.
        Output: Liste der Peak‑Indizes."""
        self.peaks = peak_detection(
            self.df["Messwerte in mV"],
            threshold,
            respacing_factor
        )
        return self.peaks
    def calculate_hrv_rmssd(self):
        peaks = self.find_peaks()
        if len(peaks) < 3:
            return None

        rr = np.diff(peaks)
        rmssd = np.sqrt(np.mean(np.square(np.diff(rr))))
        return rmssd
    
    def estimate_hr(self) -> float:
        # Peaks sicherstellen
        if not hasattr(self, "peaks"):
            self.find_peaks()

        # Peak-Zeitpunkte holen
        peak_times = self.df.loc[self.peaks, "Zeit in ms"].values

        # RR-Intervalle berechnen
        rr_intervals = np.diff(peak_times)

        # Realistische RR-Intervalle filtern (entspricht 35–210 bpm)
        rr_filtered = rr_intervals[(rr_intervals > 140) & (rr_intervals < 900)]

        if len(rr_filtered) == 0:
            return float("nan")

        avg_rr = np.mean(rr_filtered)

        bpm = 60000.0 / avg_rr
        return float(bpm)

    def plot_with_peaks(self):
        """Input: keine.
        Output: Plot des EKG‑Signals mit markierten Peaks.
        """
        if not hasattr(self, "peaks"):
            self.find_peaks()

        plot_df = self.df.head(2000)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=plot_df["Zeit in ms"],
            y=plot_df["Messwerte in mV"],
            mode='lines', name='EKG'
        ))

        peak_indices = [i for i in self.peaks if i in plot_df.index]
        if peak_indices:
            fig.add_trace(go.Scatter(
                x=plot_df["Zeit in ms"].loc[peak_indices],
                y=plot_df["Messwerte in mV"].loc[peak_indices],
                mode="markers", marker=dict(color = "red", size=6), 
                name="Peaks"
            ))

        if not plot_df.empty:
            fig.update_xaxes(range=[plot_df["Zeit in ms"].iloc[0], plot_df["Zeit in ms"].iloc[-1]])

        fig.update_layout(
            title=f"EKG Signal {self.id} mit Peaks",
            xaxis_title="Zeit in ms",
            yaxis_title="Messwerte in mV",
            height=500
        )
        return fig
    
    def plot_with_peaks_window(self, start_min=0, end_min=None):
        if not hasattr(self, "peaks"):
            self.find_peaks()

        time_ms_relative = self.df["Zeit in ms"] - self.df["Zeit in ms"].iloc[0]
        time_min = time_ms_relative / 1000 / 60

        if end_min is None:
            end_min = time_min.iloc[-1]

        mask = (time_min >= start_min) & (time_min <= end_min)
        plot_df = self.df[mask]
        time_sec = time_ms_relative[mask] / 1000

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=time_sec,
            y=plot_df["Messwerte in mV"],
            mode='lines',
            name='EKG',
            line=dict(color='steelblue')
        ))

        peak_indices = [i for i in self.peaks if i in plot_df.index]
        if peak_indices:
            fig.add_trace(go.Scatter(
                x=time_sec.loc[peak_indices],
                y=plot_df["Messwerte in mV"].loc[peak_indices],
                mode="markers",
                marker=dict(color="red", size=6),
                name="Peaks"
            ))

        start_sec = start_min * 60
        tick_vals = [start_sec + i for i in range(5)]
        tick_text = [f"{int(v//60)}m {int(v%60)}s" for v in tick_vals]

        fig.update_layout(
            title=f"EKG Signal {self.id} mit Peaks",
            xaxis=dict(
                title="Zeit",
                tickvals=tick_vals,
                ticktext=tick_text,
            ),
            yaxis_title="Messwerte in mV",
            height=500,
        )
        return fig
    
    def get_duration_minutes(self) -> float:
        time_ms = self.df["Zeit in ms"]
        duration_ms = time_ms.iloc[-1] - time_ms.iloc[0]
        return round(duration_ms / 1000 / 60, 2)