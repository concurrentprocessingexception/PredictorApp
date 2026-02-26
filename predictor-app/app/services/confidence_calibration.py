def calibrate_confidence(
    *,
    base_score: int,
    error_metrics: dict | None,
    active_model: str | None = None,
    recommended_model: str | None = None,
):
    """
    Adjust confidence score using:
    - empirical error metrics (Step 4A)
    - model recommendation alignment (Step 4C)
    """

    score = base_score
    reasons = []

    # -----------------------------
    # Step 4A — Performance penalties
    # -----------------------------
    if error_metrics:
        count = error_metrics.get("count", 0)

        if count >= 5:
            mape = error_metrics.get("mape")
            coverage = error_metrics.get("interval_coverage")

            if mape is not None:
                if mape > 0.15:
                    score -= 30
                    reasons.append("HIGH_MAPE")
                elif mape > 0.10:
                    score -= 20
                    reasons.append("ELEVATED_MAPE")
                elif mape > 0.05:
                    score -= 10
                    reasons.append("MODERATE_MAPE")
        else:
            reasons.append("INSUFFICIENT_HISTORY")

        if coverage is not None:
            if coverage < 0.3:
                score -= 30
                reasons.append("POOR_COVERAGE")
            elif coverage < 0.5:
                score -= 20
                reasons.append("LOW_COVERAGE")
            elif coverage < 0.7:
                score -= 10
                reasons.append("WEAK_COVERAGE")

    # -----------------------------
    # Step 4C — Model alignment
    # -----------------------------
    if recommended_model and active_model:
        if recommended_model != active_model:
            score -= 15
            reasons.append("MODEL_NOT_RECOMMENDED")

    # Clamp
    score = max(20, min(100, score))

    return score, reasons