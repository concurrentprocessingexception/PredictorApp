from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseForecaster(ABC):
    """
    All forecasting models (baseline, prophet, future ML)
    MUST implement this interface.
    """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Human-readable model name"""
        pass

    @property
    @abstractmethod
    def model_version(self) -> str:
        """Model version for reproducibility"""
        pass

    @abstractmethod
    def train(self, data: Any) -> None:
        """Train model using historical price data"""
        pass

    @abstractmethod
    def forecast(self, horizon: int) -> List[Dict]:
        """
        Return list of dicts:
        [
          {
            "date": <date>,
            "yhat": <float>,
            "yhat_lower": <float | None>,
            "yhat_upper": <float | None>,
            "scenario": "BASE" | "BULL" | "BEAR"
          }
        ]
        """
        pass