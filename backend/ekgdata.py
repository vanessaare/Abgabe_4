import pandas as pd
import plotly.express as px
import numpy as np
from funktionen.peak_detection import peak_detection


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

    def find_peaks(self, threshold=0.5, respacing_factor=5):
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
    
    def estimate_hr(self):
        """Input: keine (beinhaltet erkannte Peaks).
        Output: Geschätzte Herzfrequenz in BPM.
        """
        if not hasattr(self, "peaks"):
            self.find_peaks()
        peak_times = self.df["Zeit in ms"].iloc[self.peaks].values
        rr_intervals = np.diff(peak_times)  
        avg_rr = np.mean(rr_intervals)
        bpm = 30000 / avg_rr  
        return bpm
    


    def plot_with_peaks(self):
        """Input: keine.
        Output: Plot des EKG‑Signals mit markierten Peaks.
        """
        if not hasattr(self, "peaks"):
            self.find_peaks()

        plot_df = self.df.head(2000)
        fig = px.line(
            plot_df,
            x="Zeit in ms",
            y="Messwerte in mV",
            title=f"EKG Signal {self.id} mit Peaks"
        )

        peak_indices = [i for i in self.peaks if i < len(plot_df)]
        if peak_indices:
            fig.add_scatter(
                x=plot_df["Zeit in ms"].iloc[peak_indices],
                y=plot_df["Messwerte in mV"].iloc[peak_indices],
                mode="markers",
                marker=dict(color="red", size=6),
                name="Peaks"
            )

        if not plot_df.empty:
            fig.update_xaxes(
                range=[plot_df["Zeit in ms"].iloc[0], plot_df["Zeit in ms"].iloc[-1]]
            )

        fig.update_layout(
            xaxis_title="Zeit in ms",
            yaxis_title="Messwerte in mV",
            height=500,
        )

        return fig