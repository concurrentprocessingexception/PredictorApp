from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.forecast_run import ForecastRun
from app.models.forecast_point import ForecastPoint
from app.models.stock_price import StockPrice


def get_forecast_evaluation(db: Session, symbol: str, model: str):

    today = date.today()

    start_date = today - timedelta(days=5)
    end_date = today - timedelta(days=1)

    rows = (
        db.query(
            ForecastPoint.forecast_date,
            ForecastPoint.predicted_price,
            StockPrice.close.label("actual_price"),
        )
        .join(ForecastRun, ForecastRun.id == ForecastPoint.forecast_run_id)
        .join(
            StockPrice,
            (StockPrice.symbol == symbol)
            & (func.date(StockPrice.timestamp) == ForecastPoint.forecast_date),
        )
        .filter(
            ForecastRun.symbol == symbol,
            ForecastRun.model_name == model,
            ForecastRun.horizon_days == 5,
            ForecastRun.status == "SUCCESS",
            ForecastPoint.forecast_date >= start_date,
            ForecastPoint.forecast_date <= end_date,
        )
        .order_by(ForecastPoint.forecast_date.asc())
        .all()
    )

    results = []

    for r in rows:
        results.append(
            {
                "date": r.forecast_date,
                "actual_price": r.actual_price,
                "predicted_price": r.predicted_price,
            }
        )

    return results