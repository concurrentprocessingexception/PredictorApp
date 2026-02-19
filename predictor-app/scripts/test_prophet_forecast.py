from sqlalchemy.orm import Session
from database import SessionLocal
from forecasting.repository import get_historical_close_prices
from forecasting.utils import to_prophet_dataframe
from forecasting.prophet_model import ProphetForecaster


def main():
    symbol = "TSLA"
    interval = "1d"
    horizon = 30

    db: Session = SessionLocal()
    try:
        rows = get_historical_close_prices(db, symbol, interval)

        if len(rows) < 60:
            raise RuntimeError(
                f"Not enough data for forecasting. Found {len(rows)} rows."
            )

        print(f"Loaded {len(rows)} historical rows for {symbol}")

        df = to_prophet_dataframe(rows)

        print("Sample training data:")
        print(df.head())

        forecaster = ProphetForecaster()
        forecaster.train(df)

        forecast = forecaster.forecast(horizon)

        print("\nForecast output:")
        for row in forecast:
            print(
                f"{row['ds'].date()} | "
                f"yhat={row['yhat']:.2f} "
                f"[{row['yhat_lower']:.2f}, {row['yhat_upper']:.2f}]"
            )

    finally:
        db.close()


if __name__ == "__main__":
    main()
