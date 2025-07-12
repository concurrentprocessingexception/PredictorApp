from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from news import get_company_news
from db import SessionLocal
from models import stock, news
from upload import router as upload_router
from history import router as history_router
from typing import List
from fastapi import Query

import yfinance as yf
import os


app = FastAPI()

#CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Register Routes
app.include_router(history_router)
# Only include if UPLOAD_ENABLED is set
if os.getenv("UPLOAD_ENABLED") == "true":
    app.include_router(upload_router)

@app.get("/stock/{symbol}")
def get_stock_price(
    symbol: str,
    range: str = Query("1w", enum=["1d", "1w", "1m", "6m", "1y"])
):
    period_map = {
        "1d": ("1d", "5m"),
        "1w": ("5d", "15m"),
        "1m": ("1mo", "60m"),
        "6m": ("6mo", "1d"),
        "1y": ("1y", "1d"),
    }

    yf_period, interval = period_map.get(range, ("1d", "5m"))

    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=yf_period, interval=interval)

        if hist.empty:
            raise HTTPException(status_code=404, detail="No data found for given range")

        result = [
            {"date": i.strftime("%Y-%m-%d %H:%M"), "close": round(c, 2)}
            for i, c in zip(hist.index, hist["Close"])
        ]

        return {
            "symbol": symbol.upper(),
            "range": range,
            "data": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/news/{symbol}")
def news(symbol: str):
    return get_company_news(symbol.upper())
