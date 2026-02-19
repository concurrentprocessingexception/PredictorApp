# DEPRECATED: Use /fetch-historical instead
# This route is kept for legacy CSV uploads or testing purposes.

from fastapi import UploadFile, File, APIRouter, Depends, HTTPException
import pandas as pd
from sqlalchemy.orm import Session
from database import SessionLocal
from models.stock import StockPrice
from io import StringIO
from datetime import datetime

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/upload-stock-csv")
async def upload_stock_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    try:
        content = await file.read()
        df = pd.read_csv(StringIO(content.decode("utf-8")))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")

    required_columns = {"symbol", "timestamp", "close"}
    if not required_columns.issubset(df.columns):
        raise HTTPException(status_code=400, detail=f"CSV must contain columns: {required_columns}")

    inserted = 0
    skipped = 0

    for _, row in df.iterrows():
        try:
            symbol = str(row["symbol"]).upper()
            timestamp = pd.to_datetime(row["timestamp"])
            close = float(row["close"])

            exists = db.query(StockPrice).filter_by(symbol=symbol, timestamp=timestamp).first()
            if exists:
                skipped += 1
                continue

            stock = StockPrice(symbol=symbol, timestamp=timestamp, close=close)
            db.add(stock)
            inserted += 1

        except Exception as e:
            skipped += 1  # skip rows with any issues

    db.commit()

    return {
        "inserted": inserted,
        "skipped": skipped,
        "message": "Upload complete."
    }
