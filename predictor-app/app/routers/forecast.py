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
from app.schemas.forecast_evaluation import ForecastEvaluationPoint
from app.services.forecast_evaluation_service import get_forecast_evaluation
from app.services.forecast_history_service import get_forecast_history

router = APIRouter(prefix="/forecast", tags=["Forecast"])


@router.get("/history/{symbol}")
def forecast_history(
    symbol: str, 
    model: str, 
    horizon_days: int | None = None,
    db: Session = Depends(get_db)):
    """
    Returns last 30 days of forecast runs for a symbol
    """
    return get_forecast_history(db, symbol.upper(), model, horizon_days)

@router.get("/evaluation/{symbol}", response_model=list[ForecastEvaluationPoint])
def forecast_evaluation(
    symbol: str,
    model: str,
    db: Session = Depends(get_db),
):
    """
    Compare predicted vs actual prices for the latest successful forecast run.
    Always evaluates the 5-day horizon.
    """

    return get_forecast_evaluation(db, symbol.upper(), model)

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
    model: str = "baseline",
    db: Session = Depends(get_db),
):
    symbol = symbol.upper()

    forecasts = get_latest_forecasts_all_horizons(db, symbol.upper(), model)
    if not forecasts:
        return {"error": "No forecasts available"}

    trust = compare_horizons(forecasts)

    return {
        "symbol": symbol,
        "horizons": list(forecasts.keys()),
        "forecasts": forecasts,
        "trust": trust,
    }