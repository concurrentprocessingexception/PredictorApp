import pandas as pd

from app.forecasting.baseline_model import NaiveBaselineForecaster
from app.forecasting.prophet_model import ProphetForecaster


def run_forecast(
    historical_prices: pd.DataFrame,
    model_type: str,
    horizon_days: int,
):
    """
    Orchestrates forecasting.

    model_type: 'baseline' | 'prophet'
    """

    if model_type == "baseline":
        model = NaiveBaselineForecaster()
    elif model_type == "prophet":
        model = ProphetForecaster()
    else:
        raise ValueError(f"Unsupported model_type: {model_type}")

    model.train(historical_prices)
    forecast = model.forecast(horizon_days)

    return {
        "model_name": model.model_name,
        "model_version": model.model_version,
        "results": forecast,
    }