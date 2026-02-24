from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.forecast_run import ForecastRun
from app.models.forecast_point import ForecastPoint
from app.models.forecast_interval import ForecastInterval
from app.config.forecast_config import DEFAULT_HORIZONS


def get_latest_forecast_for_horizon(
    db: Session,
    symbol: str,
    horizon_days: int,
    model_name: str,
):
    run = (
        db.query(ForecastRun)
        .filter(
            ForecastRun.symbol == symbol,
            ForecastRun.horizon_days == horizon_days,
            ForecastRun.model_name == model_name,
            ForecastRun.status == "SUCCESS",
        )
        .order_by(desc(ForecastRun.created_at))
        .first()
    )

    if not run:
        return None

    points = (
        db.query(ForecastPoint)
        .filter(ForecastPoint.forecast_run_id == run.id)
        .order_by(ForecastPoint.forecast_date.asc())
        .all()
    )

    intervals = (
        db.query(ForecastInterval)
        .filter(ForecastInterval.forecast_run_id == run.id)
        .all()
    )

    interval_map = {
        i.forecast_date: i for i in intervals
    }

    series = []
    for p in points:
        band = interval_map.get(p.forecast_date)
        series.append({
            "date": p.forecast_date,
            "price": p.predicted_price,
            "lower": band.lower_bound if band else None,
            "upper": band.upper_bound if band else None,
        })

    return {
        "symbol": symbol,
        "model": run.model_name,
        "horizon_days": horizon_days,
        "created_at": run.created_at,
        "series": series,
    }


def get_latest_forecasts_all_horizons(
    db: Session,
    symbol: str,
    model_name: str,
):
    results = {}

    for horizon in DEFAULT_HORIZONS:
        forecast = get_latest_forecast_for_horizon(
            db, symbol, horizon, model_name
        )
        if forecast:
            results[horizon] = forecast

    return results