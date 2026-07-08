def peak_detection(series, threshold, respacing_factor):
    """Findet Peaks in einer gegebenen Serie basierend auf den angegebenen Parametern."""

    series = series.iloc[::respacing_factor]
    series = series[series > threshold]

    peaks = []
    last = 0
    current = 0
    next_val = 0

    for index, row in series.items():
        last = current
        current = next_val
        next_val = row

        if last < current and current > next_val and current > threshold:
            peaks.append(index - respacing_factor)

    return peaks
