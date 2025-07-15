from sqlalchemy import Column, Integer, String, Float, DateTime
from db import Base

class StockPrice(Base):
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    timestamp = Column(DateTime, index=True)
    close = Column(Float)
