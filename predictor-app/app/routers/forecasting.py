from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd

from app.database import get_db
from app.models.stock_price import StockPrice
from app.models.forecast_run import ForecastRun
from app.services.forecast_engine import run_and_persist_forecast
from app.config.forecast_config import DEFAULT_HORIZONS
from app.schemas.forecasting import InitiateForecastRequest

router = APIRouter(prefix="/forecasting", tags=["Forecasting"])


@router.post("/run")
def initiate_forecast_run(
    request: InitiateForecastRequest,
    db: Session = Depends(get_db),
):
    symbol = request.symbol.upper()
    model = request.model.lower()

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
        raise HTTPException(
            status_code=404,
            detail=f"No historical prices found for {symbol}",
        )

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
        try:
            # 🔑 SINGLE SOURCE OF TRUTH
            run = run_and_persist_forecast(
                db=db,
                symbol=symbol,
                historical_df=df,
                model_type=model,
                horizon_days=horizon,
                run_type="MANUAL",
            )

            results.append(
                {
                    "run_id": run.id,
                    "horizon_days": horizon,
                    "status": "completed",
                }
            )

        except Exception as e:
            results.append(
                {
                    "horizon_days": horizon,
                    "status": "failed",
                    "error": str(e),
                }
            )

    return {
        "symbol": symbol,
        "model": model,
        "horizons": DEFAULT_HORIZONS,
        "runs": results,
    }


@router.get("/runs")
def list_forecast_runs(
    limit: int = 20,
    db: Session = Depends(get_db),
):
    runs = (
        db.query(ForecastRun)
        .order_by(ForecastRun.created_at.desc())
        .limit(limit)
        .all()
    )

    def map_status(status: str):
        if status == "SUCCESS":
            return "completed"
        if status == "FAILED":
            return "failed"
        return "running"

    return [
        {
            "run_id": r.id,
            "symbol": r.symbol,
            "model": r.model_name,
            "horizon_days": r.horizon_days,
            "status": map_status(r.status),
            "started_at": r.created_at,
            "completed_at": r.created_at,
            "error_message": r.error_message,
        }
        for r in runs
    ]