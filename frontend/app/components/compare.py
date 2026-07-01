import math
import numpy as np

import plotly.graph_objects as go

from backend.loader import load_test


def get_metric_value(person, selected_test, metric):
    if metric == "HR_max":
        return f"{person.calc_max_heart_rate():.0f} bpm"

    test_dict = _parse_test_selection(person, selected_test)
    if test_dict is None:
        return "keine Daten"

    if metric == "Durchschnittspuls":
        hr = test_dict.get("average_hr")
        if hr is not None and not math.isnan(hr):
            return f"{hr:.2f} bpm"
        try:
            hr_value = load_test(test_dict).estimate_hr()
            if hr_value is None or math.isnan(hr_value):
                return "nicht berechnet"
            return f"{hr_value:.2f} bpm"
        except Exception:
            return "nicht berechnet"

    if metric == "HRV RMSSD":
        hrv = test_dict.get("hrv_rmssd")
        if hrv is not None and not math.isnan(hrv):
            return f"{hrv:.2f} ms"
        try:
            ekg = load_test(test_dict)
            hrv_value = ekg.calculate_hrv_rmssd()
            if hrv_value is None or (isinstance(hrv_value, float) and math.isnan(hrv_value)):
                return "nicht berechnet"
            return f"{hrv_value:.2f} ms"
        except Exception:
            return "nicht berechnet"

    if metric == "EKG":
        test_df = _get_test_dataframe(person, selected_test)
        if test_df is None:
            return "keine Daten"
        duration = (test_df.iloc[-1, 1] - test_df.iloc[0, 1]) / 1000.0
        samples = len(test_df)
        return f"{duration:.1f}s / {samples} Samples"

    return "unbekannt"


def _parse_test_selection(patient, selected_test):
    if not selected_test or selected_test == "Keine Tests verfügbar":
        return None

    if isinstance(selected_test, dict):
        return selected_test

    parts = selected_test.split()
    if len(parts) >= 2 and parts[0] == "Test":
        test_id = parts[1]
        return next((t for t in patient.ekg_tests if str(t["id"]) == test_id), patient.ekg_tests[0])

    return patient.ekg_tests[0]


def _format_time_ticks(time):
    if len(time) == 0:
        return [], []

    duration = time[-1]
    if duration <= 10:
        step = 2
    elif duration <= 30:
        step = 5
    elif duration <= 120:
        step = 10
    elif duration <= 300:
        step = 30
    else:
        step = max(60, int(duration // 5))

    tick_vals = np.arange(0, duration + step, step)
    tick_text = [f"{int(t // 60)}m {int(t % 60)}s" for t in tick_vals]
    return tick_vals, tick_text


def _prepare_signal(df):
    time = df.iloc[:, 1].astype(float).to_numpy()
    voltage = df.iloc[:, 0].astype(float).to_numpy()

    time = (time - time[0]) / 1000.0
    baseline = np.mean(voltage[: min(200, len(voltage))]) if len(voltage) else 0.0
    voltage = voltage - baseline

    scale = np.max(np.abs(voltage))
    if scale > 0:
        voltage = voltage / scale

    return time, voltage


def _get_test_dataframe(patient, selected_test=None):
    if hasattr(patient, "ekg_data") and getattr(patient.ekg_data, "df", None) is not None:
        return patient.ekg_data.df

    if hasattr(patient, "ekg_tests") and patient.ekg_tests:
        test_dict = _parse_test_selection(patient, selected_test)
        if test_dict is None:
            return None
        test_data = load_test(test_dict)
        return test_data.df

    return None


def _window_dataframe(df, start_sec=0, window_sec=None):
    if window_sec is None or df is None or df.shape[0] == 0:
        return df

    time_ms = df.iloc[:, 1].astype(float)
    start_ms = time_ms.iloc[0] + start_sec * 1000.0
    end_ms = start_ms + window_sec * 1000.0
    mask = (time_ms >= start_ms) & (time_ms <= end_ms)
    return df.loc[mask].reset_index(drop=True)


def get_test_duration_seconds(patient, selected_test=None):
    df = _get_test_dataframe(patient, selected_test)
    if df is None or df.shape[0] == 0:
        return 0
    duration_ms = float(df.iloc[-1, 1]) - float(df.iloc[0, 1])
    return duration_ms / 1000.0


def get_window_seconds(patient, selected_test=None):
    test_dict = _parse_test_selection(patient, selected_test)
    if test_dict is None:
        return 4
    if test_dict.get("result_link", "").endswith(".fit"):
        return 60
    return 4


def _window_signal(time, voltage, start_sec=0, window_sec=None):
    if window_sec is None:
        return time, voltage
    end_sec = start_sec + window_sec
    mask = (time >= start_sec) & (time <= end_sec)
    if not np.any(mask):
        return np.array([]), np.array([])
    return time[mask] - start_sec, voltage[mask]


def plot_ekg_overlay(patient_a, patient_b, selected_test_a=None, selected_test_b=None, start_sec=0, window_sec=None, label_a=None, label_b=None, title=None):
    df_a = _get_test_dataframe(patient_a, selected_test_a)
    df_b = _get_test_dataframe(patient_b, selected_test_b)

    if df_a is None or df_b is None:
        raise ValueError("Für beide Patienten müssen EKG-Daten vorhanden sein.")

    time_a, voltage_a = _prepare_signal(df_a)
    time_b, voltage_b = _prepare_signal(df_b)

    time_a, voltage_a = _window_signal(time_a, voltage_a, start_sec, window_sec)
    time_b, voltage_b = _window_signal(time_b, voltage_b, start_sec, window_sec)

    fig = go.Figure()

    trace_name_a = label_a or patient_a.get_full_name()
    trace_name_b = label_b or patient_b.get_full_name()

    fig.add_trace(go.Scatter(
        x=time_a,
        y=voltage_a,
        mode="lines",
        name=trace_name_a,
        line=dict(color="#2563eb", width=2),
        opacity=0.8,
    ))

    fig.add_trace(go.Scatter(
        x=time_b,
        y=voltage_b,
        mode="lines",
        name=trace_name_b,
        line=dict(color="#dc2626", width=2),
        opacity=0.8,
    ))

    tick_vals, tick_text = _format_time_ticks(time_a)

    fig.update_layout(
        title=title or "EKG-Vergleich für zwei Patienten",
        xaxis=dict(
            title="Zeit (s)",
            tickvals=tick_vals,
            ticktext=tick_text,
            showgrid=True,
            zeroline=False,
        ),
        yaxis_title="Normalisierte Spannung",
        legend_title="Kurven",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white",
        height=520,
        margin=dict(l=40, r=20, t=80, b=40),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),
        xaxis_range=[0, window_sec] if window_sec is not None else None,
    )

    return fig, None



