import pandas as pd
import plotly.express as px
import numpy as np
from funktionen.peak_detection import peak_detection

class EKGdata:
    def __init__(self, ekg_dict):
        #pass
        self.id = ekg_dict["id"]
        self.date = ekg_dict["date"]
        self.data = ekg_dict["result_link"]
        self.df = pd.read_csv(self.data, sep='\t', header=None, names=['Messwerte in mV','Zeit in ms',])
        self.df = self.df.iloc[:5000]  

    @staticmethod
    def load_by_id(test_id: int, person_database: list):
        for person in person_database:
            for test in person.get("ekg_tests", []):
                if test["id"] == test_id:
                    return EKGdata(test) 
        return None

    def plot_time_series(self):
        self.fig = px.line(
            self.df.head(2000),
            x="Zeit in ms",
            y="Messwerte in mV",
            title=f"EKG Signal {self.id}"
        )
        return self.fig

    def find_peaks(self, threshold=0.5, respacing_factor=5):
        self.peaks = peak_detection(
            self.df["Messwerte in mV"],
            threshold,
            respacing_factor
        )
        return self.peaks
    
    def estimate_hr(self):
        if not hasattr(self, "peaks"):
            self.find_peaks()
        peak_times = self.df["Zeit in ms"].iloc[self.peaks].values
        rr_intervals = np.diff(peak_times)  
        avg_rr = np.mean(rr_intervals)
        bpm = 60000 / avg_rr  
        return bpm
    


    def plot_with_peaks(self):
        if not hasattr(self, "peaks"):
            self.find_peaks()

        fig = px.line(
            self.df.head(2000),
            x="Zeit in ms",
            y="Messwerte in mV"
        )
        fig.add_scatter(
            x=self.df["Zeit in ms"].iloc[self.peaks],
            y=self.df["Messwerte in mV"].iloc[self.peaks],
            mode="markers",
            name="Peaks"
        )

        return fig