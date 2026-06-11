import pandas as pd
import plotly.express as px
from scipy.signal import find_peaks
import numpy as np

class EKGdata:
    def __init__(self, ekg_dict):
        #pass
        self.id = ekg_dict["id"]
        self.date = ekg_dict["date"]
        self.data = ekg_dict["result_link"]
        self.df = pd.read_csv(self.data, sep='\t', header=None, names=['Messwerte in mV','Zeit in ms',])
        self.df = self.df.iloc[:5000]  

    def plot_time_series(self):
        self.fig = px.line(
            self.df.head(2000),
            x="Zeit in ms",
            y="Messwerte in mV",
            title=f"EKG Signal {self.id}"
        )
        return self.fig

    def find_peaks(self, height=0.5, distance=200):
        self.peaks, _ = find_peaks(self.df["Messwerte in mV"],height=height, distance=distance)
        return self.peaks
    
    def calculate_heart_rate(self):
        if not hasattr(self, "peaks"):
            self.find_peaks()
        peak_times = self.df["Zeit in ms"].iloc[self.peaks].values
        rr_intervals = np.diff(peak_times)  
        avg_rr = np.mean(rr_intervals)
        bpm = 60000 / avg_rr  
        return bpm
    
    def plot_with_peaks(self):
        fig = px.line(
            self.df.head(2000),
            x="Zeit in ms",
            y="Messwerte in mV"
        )
        if hasattr(self, "peaks"):
            fig.add_scatter(
                x=self.df["Zeit in ms"].iloc[self.peaks],
                y=self.df["Messwerte in mV"].iloc[self.peaks],
                mode="markers",
                name="Peaks"
            )
        return fig