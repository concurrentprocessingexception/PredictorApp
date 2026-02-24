from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from app.database import Base

class StockPrice(Base):
    __tablename__ = "stock_prices"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)  # EOD date

    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    adj_close = Column(Float)
    volume = Column(Integer)

    interval = Column(String, nullable=False, default="1d")

    __table_args__ = (
        Index("uq_symbol_timestamp_interval", "symbol", "timestamp", "interval", unique=True),
    )