from datetime import timedelta
from typing import List, Dict

import pandas as pd

from app.forecasting.base import BaseForecaster


class NaiveBaselineForecaster(BaseForecaster):
    """
    Naive baseline:
    - Forecast = last observed adjusted close
    - Confidence band = +/- fixed percentage
    """

    def __init__(self, confidence_pct: float = 0.05):
        self.confidence_pct = confidence_pct
        self.last_date = None
        self.last_price = None

    @property
    def model_name(self) -> str:
        return "baseline"

    @property
    def model_version(self) -> str:
        return "1.0"

    def train(self, data: pd.DataFrame) -> None:
        """
        Expected columns:
        - trade_date
        - adj_close
        """
        if data.empty:
            raise ValueError("Training data is empty")

        last_row = data.sort_values("trade_date").iloc[-1]
        self.last_date = last_row["trade_date"]
        self.last_price = float(last_row["adj_close"])

    def forecast(self, horizon: int) -> List[Dict]:
        if self.last_price is None:
            raise RuntimeError("Model must be trained before forecasting")

        results = []
        for i in range(1, horizon + 1):
            forecast_date = self.last_date + timedelta(days=i)

            base = self.last_price
            lower = base * (1 - self.confidence_pct)
            upper = base * (1 + self.confidence_pct)

            results.append({
                "date": forecast_date,
                "yhat": base,
                "yhat_lower": lower,
                "yhat_upper": upper,
                "scenario": "BASE",
            })

        return results