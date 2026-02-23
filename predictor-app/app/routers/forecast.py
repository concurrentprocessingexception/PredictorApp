# app/routers/forecast.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import pandas as pd

from app.database import get_db
from app.models.stock_price import StockPrice
from app.services.forecast_engine import run_forecast

router = APIRouter(prefix="/forecast", tags=["Forecast"])


@router.post("/run")
def run_forecast_endpoint(
    symbol: str,
    model_type: str = "baseline",
    horizon_days: int = 5,
    db: Session = Depends(get_db),
):
    prices = (
        db.query(StockPrice)
        .filter(
            StockPrice.symbol == symbol,
            StockPrice.interval == "1d",
        )
        .order_by(StockPrice.timestamp)
        .all()
    )

    if not prices:
        return {"error": "No historical prices found"}

    df = pd.DataFrame(
        [
            {
                "trade_date": p.timestamp.date(),
                "adj_close": p.adj_close,
            }
            for p in prices
        ]
    )

    forecast_output = run_forecast(
        historical_prices=df,
        model_type=model_type,
        horizon_days=horizon_days,
    )

    return forecast_output