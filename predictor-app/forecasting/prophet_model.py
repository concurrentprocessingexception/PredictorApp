# Prophet-specific logic

from prophet import Prophet
from forecasting.base import BaseForecaster

class ProphetForecaster(BaseForecaster):

    def __init__(self):
        self.model = Prophet()
        self.trained = False

    def train(self, data):
        """
        data: pandas DataFrame with columns [ds, y]
        """
        self.model.fit(data)
        self.trained = True

    def forecast(self, horizon: int):
        if not self.trained:
            raise RuntimeError("Model must be trained before forecasting")

        future = self.model.make_future_dataframe(periods=horizon)
        forecast = self.model.predict(future)

        return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(horizon).to_dict("records")
