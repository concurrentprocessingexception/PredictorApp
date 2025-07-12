from sqlalchemy import Column, Integer, String, Numeric, DateTime, UniqueConstraint
from db import Base

class StockPrice(Base):
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    timestamp = Column(DateTime, index=True)
    close = Column(Numeric)

    __table_args__ = (UniqueConstraint('symbol', 'timestamp', name='uix_symbol_timestamp'),)
