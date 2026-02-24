
def compute_direction(series):
    if len(series) < 2:
        return "FLAT"

    start = series[0]["price"]
    end = series[-1]["price"]

    if end > start:
        return "UP"
    elif end < start:
        return "DOWN"
    return "FLAT"


def compute_band_width(series):
    widths = []
    for p in series:
        if p["lower"] is not None and p["upper"] is not None:
            widths.append(p["upper"] - p["lower"])
    return sum(widths) / len(widths) if widths else None


def compare_horizons(forecasts: dict):
    """
    forecasts: {horizon: forecast_data}
    """
    comparison = {}

    directions = {}

    for horizon, data in forecasts.items():
        series = data["series"]
        direction = compute_direction(series)
        band_width = compute_band_width(series)

        comparison[horizon] = {
            "direction": direction,
            "avg_band_width": band_width,
        }

        directions[horizon] = direction

    # Agreement logic
    unique_dirs = set(directions.values())
    if len(unique_dirs) == 1:
        agreement = "STRONG"
    elif len(unique_dirs) == 2 and "FLAT" in unique_dirs:
        agreement = "MODERATE"
    else:
        agreement = "WEAK"

    return {
        "per_horizon": comparison,
        "agreement": agreement,
    }