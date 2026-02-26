from typing import Dict, Any

from sqlalchemy.orm import Session

from app.services.forecast_error_analytics import get_error_metrics
from app.services.confidence_calibration import calibrate_confidence
from app.services.model_comparison import compare_models_for_horizon


def compare_horizons(
    forecasts: Dict[int, Any],
    *,
    db: Session | None = None,
    symbol: str | None = None,
    model_name: str | None = None,
):
    """
    Compare forecast horizons and compute trust / confidence.

    This function produces:
    - horizon agreement (model-based)
    - base confidence score
    - performance-calibrated confidence score (Step 4A)

    forecasts:
        {
          5: { "series": [...] },
          10: { "series": [...] },
          20: { "series": [...] }
        }
    """

    horizons = sorted(forecasts.keys())

    # ------------------------------------------------------------
    # Step 1: Model-based agreement (existing logic)
    # ------------------------------------------------------------

    if len(horizons) < 2:
        base_score = 60
        agreement = "WEAK"
    else:
        last_values = [
            forecasts[h]["series"][-1]["price"]
            for h in horizons
            if forecasts[h]["series"]
        ]

        spread = max(last_values) - min(last_values)
        avg_price = sum(last_values) / len(last_values)

        if avg_price == 0:
            agreement = "WEAK"
            base_score = 60
        else:
            spread_pct = spread / avg_price

            if spread_pct < 0.03:
                agreement = "STRONG"
                base_score = 100
            elif spread_pct < 0.07:
                agreement = "MODERATE"
                base_score = 80
            else:
                agreement = "WEAK"
                base_score = 60

    trust = {
        "agreement": agreement,
        "base_score": base_score,
        "final_score": base_score,
        "calibration_reasons": [],
        "horizons": horizons,
    }

    # ------------------------------------------------------------
    # Step 2: Performance-based calibration (Step 4A)
    # ------------------------------------------------------------

    # We only calibrate if DB + symbol + model are provided
    if db and symbol and model_name:
        horizon_scores = {}
        calibration_notes = {}

        for horizon in horizons:
            metrics = get_error_metrics(
                db=db,
                symbol=symbol,
                model_name=model_name,
                horizon_days=horizon,
                lookback_days=30,
            )

            comparison = compare_models_for_horizon(
                db=db,
                symbol=symbol,
                horizon_days=horizon,
                lookback_days=30,
            )

            recommended_model = comparison.get("recommended_model")

            calibrated_score, reasons = calibrate_confidence(
                base_score=base_score,
                error_metrics=metrics,
                active_model=model_name,
                recommended_model=recommended_model,
            )

            horizon_scores[horizon] = calibrated_score

            calibration_notes[horizon] = {
                "metrics": metrics,
                "reasons": reasons,
                "recommended_model": recommended_model,
            }

        # Conservative aggregation:
        # use the **worst** calibrated horizon
        trust["final_score"] = min(horizon_scores.values())
        trust["calibration_reasons"] = calibration_notes

    return trust