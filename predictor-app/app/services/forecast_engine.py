import pandas as pd

from app.forecasting.baseline_model import NaiveBaselineForecaster
from app.forecasting.prophet_model import ProphetForecaster
from app.services.forecast_persistence import persist_forecast

def run_and_persist_forecast(
    *,
    db,
    symbol: str,
    historical_df,
    model_type: str,
    horizon_days: int,
    run_type: str,
):
    if model_type == "baseline":
        model = NaiveBaselineForecaster()
    elif model_type == "prophet":
        model = ProphetForecaster()
    else:
        raise ValueError(f"Unsupported model_type: {model_type}")

    model.train(historical_df)
    results = model.forecast(horizon_days)

    persist_forecast(
        db=db,
        symbol=symbol,
        model_name=model.model_name,
        model_version=model.model_version,
        horizon_days=horizon_days,
        run_type=run_type,
        train_start=historical_df["trade_date"].min(),
        train_end=historical_df["trade_date"].max(),
        results=results,
    )

    return {
        "model": model.model_name,
        "horizon_days": horizon_days,
        "status": "persisted",
    }