from pydantic import BaseModel

class InitiateForecastRequest(BaseModel):
    symbol: str
    model: str = "baseline"
    horizon: int = 5