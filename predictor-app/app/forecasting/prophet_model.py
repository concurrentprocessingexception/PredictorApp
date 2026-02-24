from prophet import Prophet
from .base import BaseForecaster
import pandas as pd
import numpy as np


class ProphetForecaster(BaseForecaster):
    model_name = "prophet"
    model_version = "1.0"

    def __init__(self):
        self.model = Prophet(
            growth="linear",
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=True,
            changepoint_prior_scale=0.03, # prevents trend whiplash
            seasonality_prior_scale=5.0, # dampens noise
            changepoint_range=0.85, # avoid overreacting to last few points
            interval_width=0.80,
        )
        self.trained = False

    def train(self, data: pd.DataFrame):
        """
        data: DataFrame with columns:
        - trade_date (date)
        - adj_close (float)
        """

        if not {"trade_date", "adj_close"}.issubset(data.columns):
            raise ValueError("Expected columns: trade_date, adj_close")

        df = data.rename(
            columns={
                "trade_date": "ds",
                "adj_close": "y",
            }
        ).copy()

        df["y"] = np.log(df["y"])

        self.model.fit(df)
        self.trained = True

    def forecast(self, horizon: int):
        if not self.trained:
            raise RuntimeError("Model must be trained before forecasting")

        future = self.model.make_future_dataframe(periods=horizon)
        forecast = self.model.predict(future)

        result = forecast.tail(horizon)

        output = []
        for _, row in result.iterrows():
            yhat = float(np.exp(row["yhat"]))
            yhat_lower = float(np.exp(row["yhat_lower"]))
            yhat_upper = float(np.exp(row["yhat_upper"]))

            output.append(
                {
                    "date": row["ds"].date(),
                    "yhat": max(0.0, yhat),
                    "yhat_lower": max(0.0, yhat_lower),
                    "yhat_upper": max(0.0, yhat_upper),
                    "scenario": "BASE",
                }
            )

        output = self._cap_daily_moves(output)
        return output
    
    def _cap_daily_moves(self, forecasts, max_daily_pct=0.05):
        if not forecasts:
            return forecasts

        capped = [forecasts[0]]

        for prev, curr in zip(forecasts, forecasts[1:]):
            max_up = prev["yhat"] * (1 + max_daily_pct)
            max_down = prev["yhat"] * (1 - max_daily_pct)

            curr["yhat"] = min(max(curr["yhat"], max_down), max_up)
            curr["yhat_lower"] = min(curr["yhat_lower"], curr["yhat"])
            curr["yhat_upper"] = max(curr["yhat_upper"], curr["yhat"])

            capped.append(curr)

        return capped