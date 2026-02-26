from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.model_comparison import compare_models_for_horizon

router = APIRouter(prefix="/models", tags=["Model Comparison"])


@router.get("/compare")
def compare_models(
    symbol: str,
    horizon_days: int,
    lookback_days: int = 30,
    db: Session = Depends(get_db),
):
    return compare_models_for_horizon(
        db=db,
        symbol=symbol.upper(),
        horizon_days=horizon_days,
        lookback_days=lookback_days,
    )