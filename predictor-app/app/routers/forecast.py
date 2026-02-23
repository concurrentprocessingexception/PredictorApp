from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import SessionLocal
from app.forecasting.repository import get_historical_close_prices
from app.forecasting.utils import to_prophet_dataframe
from app.forecasting.prophet_model import ProphetForecaster

router = APIRouter(prefix="/forecast", tags=["Forecast"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{symbol}")
def forecast_stock(
    symbol: str,
    horizon: int = 30,
    interval: str = "1d",
    db: Session = Depends(get_db),
):
    symbol = symbol.upper()

    rows = get_historical_close_prices(db, symbol, interval)

    if len(rows) < 60:
        raise HTTPException(
            status_code=400,
            detail=f"Not enough historical data to forecast {symbol}. "
                   f"Need at least 60 data points."
        )

    df = to_prophet_dataframe(rows)

    try:
        forecaster = ProphetForecaster()
        forecaster.train(df)
        forecast_rows = forecaster.forecast(horizon)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Forecasting failed: {str(e)}"
        )

    response = {
        "symbol": symbol,
        "model": "prophet",
        "interval": interval,
        "horizon": horizon,
        "generated_at": datetime.utcnow().isoformat(),
        "forecast": [
            {
                "date": row["ds"].date().isoformat(),
                "prediction": round(row["yhat"], 2),
                "lower": round(row["yhat_lower"], 2),
                "upper": round(row["yhat_upper"], 2),
            }
            for row in forecast_rows
        ],
    }

    print(f"Generated forecast for {symbol} with {len(forecast_rows)} rows.")
    print(f"Forecast response: {response}")

    return response
