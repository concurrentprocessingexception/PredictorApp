from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Literal, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.stock_price import StockPrice
from datetime import datetime
import yfinance as yf
from fastapi import Query
from sqlalchemy import and_
import pandas as pd
import logging
from app.database import get_db


router = APIRouter(prefix="/stocks/history", tags=["StocksHistory"])

# Configure logging: set level and format
logging.basicConfig(
    level=logging.INFO,  # Set the minimum log level to DEBUG
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class FetchHistoricalRequest(BaseModel):
    symbol: str
    start_date: str  # format: YYYY-MM-DD
    end_date: str    # format: YYYY-MM-DD
    interval: Literal['1d'] = '1d'


"""
    This router provides endpoints to fetch historical stock price data from yfinance 
    and store it in the database, for a given stock symbol and date range.
"""
@router.post("/")
def fetch_historical(data: FetchHistoricalRequest, db: Session = Depends(get_db)):
    symbol = data.symbol.upper()

    try:
        hist = yf.download(
            symbol,
            start=data.start_date,
            end=data.end_date,
            interval=data.interval,
            auto_adjust=False  # so Adj Close stays separate
        )
        logging.info(f"yfinance returned {hist.shape[0]} rows for {symbol}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch data: {e}")

    if hist.empty:
        raise HTTPException(status_code=404, detail="No data returned by yfinance.")

    inserted = 0
    skipped = 0

    for timestamp, row in hist.iterrows():
        timestamp = timestamp.to_pydatetime()
        
        exists = db.query(StockPrice).filter_by(
            symbol=symbol, 
            timestamp=timestamp,
            interval=data.interval
        ).first()

        if pd.isna(row.get(("Adj Close", symbol))):
            skipped += 1
            continue

        if exists:
            skipped += 1
            continue

        def safe_float(val):
            return float(val) if val is not None and not pd.isna(val) else None
        
        stock_entry = StockPrice(
            symbol=symbol,
            timestamp=timestamp,
            open=safe_float(row.get(("Open", symbol))),
            high=safe_float(row.get(("High", symbol))),
            low=safe_float(row.get(("Low", symbol))),
            close=safe_float(row.get(("Close", symbol))),
            adj_close=safe_float(row.get(("Adj Close", symbol))),
            volume=int(row.get(("Volume", symbol))) if row.get(("Volume", symbol)) and not pd.isna(row.get(("Volume", symbol))) else None,
            interval=data.interval
        )

        db.add(stock_entry)
        inserted += 1

    db.commit()

    MAX_HISTORY_DAYS = 750

    subquery = (
        select(StockPrice.id)
        .where(
            StockPrice.symbol == symbol,
            StockPrice.interval == "1d"
        )
        .order_by(StockPrice.timestamp.desc())
        .offset(MAX_HISTORY_DAYS)
    )

    db.query(StockPrice).filter(
        StockPrice.id.in_(subquery)
    ).delete(synchronize_session=False)

    db.commit()

    return {
        "symbol": symbol,
        "inserted": inserted,
        "skipped": skipped,
        "message": "Historical OHLCV data saved."
    }


@router.get("/{symbol}")
def get_stock_history(
    symbol: str,
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD"),
    interval: Literal["1d"] = "1d",
    db: Session = Depends(get_db)
):
    symbol = symbol.upper()

    query = db.query(StockPrice).filter(
        StockPrice.symbol == symbol,
        StockPrice.interval == interval
    )

    # Optional date filtering
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(StockPrice.timestamp >= start_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format")

    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            query = query.filter(StockPrice.timestamp <= end_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format")

    records = query.order_by(StockPrice.timestamp.asc()).all()

    if not records:
        raise HTTPException(status_code=404, detail="No data found for given symbol and date range")

    return [
        {
            "date": record.timestamp.isoformat(),
            "open": record.open,
            "high": record.high,
            "low": record.low,
            "close": record.close,
            "adj_close": record.adj_close,
            "volume": record.volume,
        }
        for record in records
    ]
