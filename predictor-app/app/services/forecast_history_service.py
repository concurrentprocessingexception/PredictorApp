from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.models.forecast_run import ForecastRun
from app.models.forecast_point import ForecastPoint


def get_forecast_history(
    db: Session,
    symbol: str,
    model: str,
    horizon_days: int | None = None,
):

    today = date.today()
    start_date = today - timedelta(days=30)

    query = (
        db.query(
            ForecastRun.created_at.label("run_date"),
            ForecastRun.horizon_days,
            ForecastPoint.forecast_date,
            ForecastPoint.predicted_price,
        )
        .join(ForecastPoint, ForecastRun.id == ForecastPoint.forecast_run_id)
        .filter(
            ForecastRun.symbol == symbol,
            ForecastRun.model_name == model,
            ForecastRun.status == "SUCCESS",
            ForecastRun.created_at >= start_date,
        )
    )

    # Apply horizon filter only if provided
    if horizon_days:
        query = query.filter(ForecastRun.horizon_days == horizon_days)

    rows = (
        query.order_by(ForecastPoint.forecast_date.desc())
        .all()
    )

    results = []

    for r in rows:
        results.append(
            {
                "run_date": r.run_date.strftime("%Y-%m-%d %H:%M:%S"),
                "forecast_date": r.forecast_date,
                "horizon_days": r.horizon_days,
                "predicted_price": float(r.predicted_price),
            }
        )

    return results