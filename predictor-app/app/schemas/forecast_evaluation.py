from pydantic import BaseModel
from datetime import date


class ForecastEvaluationPoint(BaseModel):
    date: date
    actual_price: float | None
    predicted_price: float

    class Config:
        orm_mode = True