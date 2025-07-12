# predictor-app/history.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Literal
from sqlalchemy.orm import Session
from db import SessionLocal
from models.stock import StockPrice
from datetime import datetime
import yfinance as yf
from fastapi import Query
from sqlalchemy import and_
from typing import Optional
from datetime import datetime

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class FetchHistoricalRequest(BaseModel):
    symbol: str
    start_date: str  # format: YYYY-MM-DD
    end_date: str    # format: YYYY-MM-DD
    interval: Literal['1d', '1h', '1wk', '1m'] = '1d'


@router.post("/fetch-historical")
def fetch_historical(data: FetchHistoricalRequest, db: Session = Depends(get_db)):
    symbol = data.symbol.upper()

    try:
        hist = yf.download(symbol, start=data.start_date, end=data.end_date, interval=data.interval)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch data: {e}")

    if hist.empty:
        raise HTTPException(status_code=404, detail="No data returned by yfinance.")

    inserted = 0
    skipped = 0

    for timestamp, row in hist.iterrows():
        timestamp = timestamp.to_pydatetime()
        close = float(row["Close"])

        exists = db.query(StockPrice).filter_by(symbol=symbol, timestamp=timestamp).first()
        if exists:
            skipped += 1
            continue

        stock_entry = StockPrice(
            symbol=symbol,
            timestamp=timestamp,
            close=close
        )
        db.add(stock_entry)
        inserted += 1

    db.commit()

    return {
        "symbol": symbol,
        "inserted": inserted,
        "skipped": skipped,
        "message": "Historical data saved to DB"
    }


@router.get("/history/{symbol}")
def get_stock_history(
    symbol: str,
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD"),
    interval: str = Query("1d", regex="^(1d|1h|1wk|1m)$"),
    db: Session = Depends(get_db)
):
    symbol = symbol.upper()

    query = db.query(StockPrice).filter(StockPrice.symbol == symbol)

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
            "date": record.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "close": record.close
        }
        for record in records
    ]
