# app/routers/forecast.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import pandas as pd

from app.database import get_db
from app.models.stock_price import StockPrice
from app.services.forecast_engine import run_and_persist_forecast
from app.config.forecast_config import DEFAULT_HORIZONS

from app.services.forecast_reader import get_latest_forecast_for_horizon
from app.services.forecast_reader import get_latest_forecasts_all_horizons
from app.services.forecast_trust import compare_horizons

router = APIRouter(prefix="/forecast", tags=["Forecast"])


@router.post("/run")
def run_forecast_endpoint(
    symbol: str,
    model_type: str = "baseline",
    db: Session = Depends(get_db),
):
    prices = (
        db.query(StockPrice)
        .filter(
            StockPrice.symbol == symbol,
            StockPrice.interval == "1d",
            StockPrice.adj_close.isnot(None),
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

    results = []
    for horizon in DEFAULT_HORIZONS:
        result = run_and_persist_forecast(
            db=db,
            symbol=symbol,
            historical_df=df,
            model_type=model_type,
            horizon_days=horizon,
            run_type="MANUAL",
        )
        results.append(result)

    return {
        "symbol": symbol,
        "model": model_type,
        "horizons": DEFAULT_HORIZONS,
        "runs": results,
    }

@router.get("/latest/{symbol}")
def get_latest_forecasts(
    symbol: str,
    db: Session = Depends(get_db),
):
    data = get_latest_forecasts_all_horizons(db, symbol.upper())

    if not data:
        return {"error": "No forecasts found"}

    return data


@router.get("/latest/{symbol}/{horizon_days}")
def get_latest_forecast_by_horizon(
    symbol: str,
    horizon_days: int,
    db: Session = Depends(get_db),
):
    data = get_latest_forecast_for_horizon(
        db, symbol.upper(), horizon_days
    )

    if not data:
        return {"error": "No forecast found"}

    return data

@router.get("/trust/{symbol}")
def get_forecast_trust(
    symbol: str,
    db: Session = Depends(get_db),
):
    forecasts = get_latest_forecasts_all_horizons(
        db, symbol.upper()
    )

    if not forecasts:
        return {"error": "No forecasts available"}

    trust = compare_horizons(forecasts)

    return {
        "symbol": symbol.upper(),
        "trust": trust,
    }

@router.get("/dashboard/{symbol}")
def get_forecast_dashboard(
    symbol: str,
    db: Session = Depends(get_db),
):
    symbol = symbol.upper()

    forecasts = get_latest_forecasts_all_horizons(db, symbol)
    if not forecasts:
        return {"error": "No forecasts available"}

    trust = compare_horizons(forecasts)

    return {
        "symbol": symbol,
        "horizons": list(forecasts.keys()),
        "forecasts": forecasts,
        "trust": trust,
    }