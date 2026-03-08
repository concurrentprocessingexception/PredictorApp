from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.forecast_error_analytics import get_error_metrics

"""
A FastAPI endpoint to get forecast error metrics (MAE, MAPE) for a given symbol/model/horizon.
"""


router = APIRouter(prefix="/forecast/metrics", tags=["Forecast Metrics"])


@router.get("/error")
def get_forecast_error_metrics(
    symbol: str,
    model_name: str,
    horizon_days: int,
    lookback_days: int = 30,
    db: Session = Depends(get_db),
):
    metrics = get_error_metrics(
        db=db,
        symbol=symbol.upper(),
        model_name=model_name,
        horizon_days=horizon_days,
        lookback_days=lookback_days,
    )

    return {
        "symbol": symbol.upper(),
        "model": model_name,
        "horizon_days": horizon_days,
        "lookback_days": lookback_days,
        "metrics": metrics,
    }