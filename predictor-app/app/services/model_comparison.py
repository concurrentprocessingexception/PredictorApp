from sqlalchemy.orm import Session

from app.services.forecast_error_analytics import get_error_metrics


def compare_models_for_horizon(
    *,
    db: Session,
    symbol: str,
    horizon_days: int,
    lookback_days: int = 30,
    min_samples: int = 5,
):
    """
    Compare Prophet vs Baseline using empirical error metrics.
    Returns a recommendation, not a forced switch.
    """

    models = ["baseline", "prophet"]
    metrics_by_model = {}

    for model in models:
        metrics = get_error_metrics(
            db=db,
            symbol=symbol,
            model_name=model,
            horizon_days=horizon_days,
            lookback_days=lookback_days,
        )
        metrics_by_model[model] = metrics

    # Guard: insufficient data
    for model, metrics in metrics_by_model.items():
        if metrics["count"] < min_samples:
            return {
                "status": "INSUFFICIENT_DATA",
                "recommended_model": None,
                "metrics": metrics_by_model,
            }

    # Primary comparison: MAE
    mae_baseline = metrics_by_model["baseline"]["mae"]
    mae_prophet = metrics_by_model["prophet"]["mae"]

    if mae_baseline is None or mae_prophet is None:
        return {
            "status": "NO_COMPARISON",
            "recommended_model": None,
            "metrics": metrics_by_model,
        }

    # Relative improvement threshold (avoid flapping)
    improvement_threshold = 0.10  # 10%

    if mae_prophet < mae_baseline * (1 - improvement_threshold):
        recommended = "prophet"
        reason = "LOWER_MAE"
    elif mae_baseline < mae_prophet * (1 - improvement_threshold):
        recommended = "baseline"
        reason = "LOWER_MAE"
    else:
        recommended = None
        reason = "NO_CLEAR_WINNER"

    return {
        "status": "OK",
        "recommended_model": recommended,
        "reason": reason,
        "metrics": metrics_by_model,
    }