import pandas as pd
import numpy as np


def evaluate_forecast_confidence(
    historical_df: pd.DataFrame,
    forecast: list[dict],
) -> dict:
    """
    Returns:
    {
      confidence_score: int (0-100),
      confidence_level: HIGH | MEDIUM | LOW,
      issues: list[str]
    }
    """

    issues = []
    score = 100

    # --- Data quality penalties ---
    row_count = len(historical_df)
    if row_count < 180:
        score -= 20
        issues.append("SHORT_HISTORY")

    na_ratio = historical_df["adj_close"].isna().mean()
    if na_ratio > 0.03:
        score -= 15
        issues.append("MISSING_VALUES")

    # --- Volatility penalty ---
    returns = historical_df["adj_close"].pct_change().dropna()
    volatility = returns.std()

    if volatility > 0.025:
        penalty = min(15, int((volatility - 0.025) * 500))
        score -= penalty
        issues.append("ELEVATED_VOLATILITY")

    # --- Forecast sanity checks ---
    yhat = np.array([f["yhat"] for f in forecast])

    # Large cumulative drift
    total_drift = abs(yhat[-1] - yhat[0]) / yhat[0]
    if total_drift > 0.15:
        penalty = min(20, int((total_drift - 0.15) * 100))
        score -= penalty
        issues.append("FORECAST_DRIFT")

    # Confidence band explosion
    band_widths = [
        f["yhat_upper"] - f["yhat_lower"] for f in forecast
    ]
    avg_band = np.mean(band_widths)
    hist_price = historical_df["adj_close"].mean()

    vol_scaled_band = avg_band / (hist_price * volatility)

    if vol_scaled_band > 3.0:
        score -= 15
        issues.append("WIDE_CONFIDENCE_BANDS")

    score = max(score, 0)

    if score >= 80:
        level = "HIGH"
    elif score >= 50:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "confidence_score": score,
        "confidence_level": level,
        "issues": issues,
    }