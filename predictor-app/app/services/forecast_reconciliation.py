from sqlalchemy.orm import Session
from datetime import date

from app.models.forecast_point import ForecastPoint
from app.models.forecast_run import ForecastRun
from app.models.forecast_interval import ForecastInterval
from app.models.forecast_error import ForecastError
from app.models.stock_price import StockPrice


"""
This module contains logic to compare forecasts with actuals and compute errors.

This function should run after actual prices are ingested (daily).
"""

def reconcile_forecasts_for_date(
    db: Session,
    *,
    symbol: str,
    target_date: date,
):
    """
    Compare forecasts made for target_date with actual price.
    """

    actual = (
        db.query(StockPrice)
        .filter(
            StockPrice.symbol == symbol,
            StockPrice.timestamp == target_date,
        )
        .one_or_none()
    )

    if not actual:
        return  # no actual yet

    forecasts = (
        db.query(ForecastPoint, ForecastRun)
        .join(ForecastRun, ForecastPoint.forecast_run_id == ForecastRun.id)
        .filter(
            ForecastRun.symbol == symbol,
            ForecastPoint.forecast_date == target_date,
            ForecastRun.status == "SUCCESS",
        )
        .all()
    )

    for fp, run in forecasts:
        error = actual.adj_close - fp.predicted_price
        abs_error = abs(error)
        pct_error = error / actual.adj_close if actual.adj_close else None

        interval = (
            db.query(ForecastInterval)
            .filter(
                ForecastInterval.forecast_run_id == run.id,
                ForecastInterval.forecast_date == target_date,
            )
            .one_or_none()
        )

        within_interval = None
        if interval:
            within_interval = (
                interval.lower_bound
                <= actual.adj_close
                <= interval.upper_bound
            )

        db.add(
            ForecastError(
                forecast_point_id=fp.id,
                symbol=symbol,
                model_name=run.model_name,
                horizon_days=run.horizon_days,
                target_date=target_date,
                actual_price=actual.adj_close,
                predicted_price=fp.predicted_price,
                error=error,
                abs_error=abs_error,
                pct_error=pct_error,
                within_interval=within_interval,
            )
        )

    db.commit()