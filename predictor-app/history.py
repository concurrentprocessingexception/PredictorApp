# predictor-app/history.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Literal
from sqlalchemy.orm import Session
from db import SessionLocal
from models.stock import StockPrice
from datetime import datetime
import yfinance as yf

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
