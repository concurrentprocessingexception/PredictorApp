import logging
import pandas as pd
from datetime import timedelta

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
    horizon_days: int | None = None,
    from_date=None,
    to_date=None,
    run_type: str,
):

    fallback_used = False
    fallback_reason = None

    # --------------------------------------------------
    # Determine forecast mode
    # --------------------------------------------------

    if from_date and to_date:
        logger.info(
            f"Running historical forecast | symbol={symbol} | "
            f"from={from_date} | to={to_date}"
        )

        from_date = pd.to_datetime(from_date).date()
        to_date = pd.to_datetime(to_date).date()

        # Prevent data leakage
        historical_df = historical_df[
            historical_df["trade_date"] < pd.to_datetime(from_date)
        ]

        horizon_days = (to_date - from_date).days + 1

    else:
        if horizon_days is None:
            raise ValueError(
                "horizon_days must be provided when from_date/to_date are not used"
            )

        logger.info(
            f"Running standard forecast | symbol={symbol} | horizon={horizon_days}d"
        )

        # derive forecast window automatically
        last_train_date = pd.to_datetime(historical_df["trade_date"].max()).date()

        from_date = last_train_date + timedelta(days=1)
        to_date = last_train_date + timedelta(days=horizon_days)

    # --------------------------------------------------
    # Model selection
    # --------------------------------------------------

    if model_type == "baseline":
        model = NaiveBaselineForecaster()

    elif model_type == "prophet":

        validation = validate_prophet_data(historical_df)

        if not validation["eligible"]:
            model = NaiveBaselineForecaster()
            fallback_used = True
            fallback_reason = validation["issues"]

            logger.info(
                f"Prophet data validation failed, falling back to baseline | "
                f"symbol={symbol} | horizon={horizon_days}d | issues={validation['issues']}"
            )

        else:
            model = ProphetForecaster()

    else:
        raise ValueError(f"Unsupported model_type: {model_type}")

    logger.info(
        f"Forecast model selected | symbol={symbol} | horizon={horizon_days}d | "
        f"final_model={model.model_name}"
    )

    # --------------------------------------------------
    # Train model
    # --------------------------------------------------

    model.train(historical_df)

    # --------------------------------------------------
    # Run forecast
    # --------------------------------------------------

    results = model.forecast(horizon_days)

    # --------------------------------------------------
    # Evaluate forecast confidence
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Persist forecast
    # --------------------------------------------------

    persist_forecast(
        db=db,
        symbol=symbol,
        model_name=model.model_name,
        model_version=model.model_version,
        horizon_days=horizon_days,
        forecast_from_date=from_date,
        forecast_to_date=to_date,
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
        "forecast_from": from_date,
        "forecast_to": to_date,
    }