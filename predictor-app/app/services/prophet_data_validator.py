import pandas as pd
import logging


logger = logging.getLogger(__name__)

def validate_prophet_data(df: pd.DataFrame) -> dict:
    """
    Determines whether Prophet is allowed to run on this dataset.

    Expected columns:
    - trade_date
    - adj_close
    """

    issues = []

    # --- Structural checks ---
    required_cols = {"trade_date", "adj_close"}
    if not required_cols.issubset(df.columns):
        return {
            "eligible": False,
            "issues": ["MISSING_REQUIRED_COLUMNS"],
        }

    # --- Volume checks ---
    row_count = len(df)
    if row_count < 120:
        issues.append("INSUFFICIENT_ROWS")

    # --- Time span checks ---
    span_days = (df["trade_date"].max() - df["trade_date"].min()).days
    if span_days < 180:
        issues.append("INSUFFICIENT_TIME_SPAN")

    # --- Missing values ---
    na_ratio = df["adj_close"].isna().mean()
    if na_ratio > 0.05:
        issues.append("TOO_MANY_MISSING_VALUES")

    # --- Zero values (illiquid assets) ---
    zero_ratio = (df["adj_close"] == 0).mean()
    if zero_ratio > 0.10:
        issues.append("TOO_MANY_ZERO_VALUES")

    return {
        "eligible": len(issues) == 0,
        "issues": issues,
    }