from pydantic import BaseModel

class InitiateForecastRequest(BaseModel):
    symbol: str
    model: str = "baseline"