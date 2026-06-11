def peak_detection(series, threshold, respacing_factor=5):
    """
    A function to find the peaks in a series
    Inputs:
        - series (pd.Series): The series to find the peaks in
        - threshold (float): The threshold for the peaks
        - respacing_factor (int): The factor to respace the series
    Outputs:
        - peaks (list): A list of the indices of the peaks
    """
    # Respace the series
    series = series.iloc[::respacing_factor]
    
    # Filter the series
    series = series[series>threshold]


    peaks = []
    last = 0
    current = 0
    next_val = 0

    for index, row in series.items():
        last = current
        current = next_val
        next_val = row

        if last < current and current > next_val and current > threshold:
            peaks.append(index-respacing_factor)

    return peaks