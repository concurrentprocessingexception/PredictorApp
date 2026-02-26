from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import date, timedelta

from app.models.forecast_error import ForecastError


"""
This module contains logic to compute error metrics (MAE, MAPE) for forecasts.
MAE - Mean Absolute Error
MAPE - Mean Absolute Percentage Error
"""

def get_error_metrics(
    db: Session,
    *,
    symbol: str,
    model_name: str,
    horizon_days: int,
    lookback_days: int = 30,
):
    """
    Compute MAE / MAPE for a given symbol, model, horizon.
    """

    start_date = date.today() - timedelta(days=lookback_days)

    q = (
        db.query(
            func.count(ForecastError.id).label("count"),
            func.avg(ForecastError.abs_error).label("mae"),
            func.avg(ForecastError.pct_error).label("mape"),
            func.avg(
                case(
                    (ForecastError.within_interval == True, 1.0),
                    else_=0.0,
                )
            ).label("interval_coverage")
        )
        .filter(
            ForecastError.symbol == symbol,
            ForecastError.model_name == model_name,
            ForecastError.horizon_days == horizon_days,
            ForecastError.target_date >= start_date,
        )
    )

    row = q.one()

    if row.count == 0:
        return {
            "count": 0,
            "mae": None,
            "mape": None,
            "interval_coverage": None,
        }

    return {
        "count": row.count,
        "mae": float(row.mae),
        "mape": float(row.mape) if row.mape is not None else None,
        "interval_coverage": float(row.interval_coverage)
        if row.interval_coverage is not None
        else None,
    }