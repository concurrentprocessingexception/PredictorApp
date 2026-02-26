from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.database import get_db
from app.services.forecast_reconciliation import reconcile_forecasts_for_date


"""
A FastAPI endpoint you can call from UI

Runs reconciliation for:
- a symbol
- a target date (or default: today)

Returns what was reconciled
"""

router = APIRouter(prefix="/reconcile", tags=["Reconciliation"])


@router.post("/run")
def run_reconciliation(
    symbol: str,
    target_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    """
    Manually reconcile forecasts with actual prices.
    """

    if target_date is None:
        target_date = date.today()

    reconcile_forecasts_for_date(
        db=db,
        symbol=symbol.upper(),
        target_date=target_date,
    )

    return {
        "status": "ok",
        "symbol": symbol.upper(),
        "target_date": target_date,
        "message": "Reconciliation completed",
    }