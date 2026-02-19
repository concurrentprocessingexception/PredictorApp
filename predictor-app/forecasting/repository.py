# Fetch historical data from DB

from sqlalchemy.orm import Session
from models.stock import StockPrice

def get_historical_close_prices(
    db: Session,
    symbol: str,
    interval: str = "1d"
):
    """
    Returns historical close prices ordered by timestamp.
    """
    return (
        db.query(StockPrice.timestamp, StockPrice.close)
        .filter(
            StockPrice.symbol == symbol,
            StockPrice.interval == interval
        )
        .order_by(StockPrice.timestamp.asc())
        .all()
    )
