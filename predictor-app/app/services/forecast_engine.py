import logging
import pandas as pd

from app.forecasting.baseline_model import NaiveBaselineForecaster
from app.forecasting.prophet_model import ProphetForecaster
from app.services.forecast_persistence import persist_forecast
from app.services.prophet_data_validator import validate_prophet_data
from app.services.forecast_confidence import evaluate_forecast_confidence


logger = logging.getLogger(__name__)

def run_and_persist_forecast(
    *,
    db,
    symbol: str,
    historical_df,
    model_type: str,
    horizon_days: int,
    run_type: str,
):
    fallback_used = False
    fallback_reason = None

    if model_type == "baseline":
        model = NaiveBaselineForecaster()

    elif model_type == "prophet":
        validation = validate_prophet_data(historical_df)

        if not validation["eligible"]:
            model = NaiveBaselineForecaster()
            fallback_used = True
            fallback_reason = validation["issues"]
            logger.info(f"Prophet data validation failed, falling back to baseline | symbol={symbol} | horizon={horizon_days}d | issues={validation['issues']}")
        else:
            model = ProphetForecaster()

    else:
        raise ValueError(f"Unsupported model_type: {model_type}")
    
    logger.info(f"Forecast model selected | symbol={symbol} | horizon={horizon_days}d | final_model={model.model_name}")

    model.train(historical_df)
    results = model.forecast(horizon_days)

    confidence = evaluate_forecast_confidence(
        historical_df=historical_df,
        forecast=results,
    )

    logger.info(
        f"Forecast confidence | symbol={symbol} | horizon={horizon_days}d | "
        f"score={confidence['confidence_score']} | level={confidence['confidence_level']}",
        extra={
            "symbol": symbol,
            "horizon_days": horizon_days,
            "confidence_score": confidence["confidence_score"],
            "confidence_level": confidence["confidence_level"],
            "issues": confidence["issues"],
        },
    )

    persist_forecast(
        db=db,
        symbol=symbol,
        model_name=model.model_name,
        model_version=model.model_version,
        horizon_days=horizon_days,
        run_type=run_type,
        train_start=historical_df["trade_date"].min(),
        train_end=historical_df["trade_date"].max(),
        results=results,
    )

    return {
        "model": model.model_name,
        "horizon_days": horizon_days,
        "status": "persisted",
        "fallback_used": fallback_used,
        "fallback_reason": fallback_reason,
        "confidence": confidence,
    }