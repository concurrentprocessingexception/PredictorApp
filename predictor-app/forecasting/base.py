# Common forecasting interface

from abc import ABC, abstractmethod
from typing import List, Dict

class BaseForecaster(ABC):

    @abstractmethod
    def train(self, data):
        """Train the model"""
        pass

    @abstractmethod
    def forecast(self, horizon: int) -> List[Dict]:
        """Return forecast for next N periods"""
        pass
