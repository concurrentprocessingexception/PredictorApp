from datetime import date
from sqlalchemy.orm import Session

from app.models.forecast_run import ForecastRun
from app.models.forecast_point import ForecastPoint
from app.models.forecast_interval import ForecastInterval
from app.config.forecast_config import FORECAST_RUN_RETENTION


def persist_forecast(
    db: Session,
    *,
    symbol: str,
    model_name: str,
    model_version: str,
    horizon_days: int,
    run_type: str,  # AUTO | MANUAL
    train_start: date,
    train_end: date,
    results: list,
):
    run = ForecastRun(
        symbol=symbol,
        model_name=model_name,
        model_version=model_version,
        horizon_days=horizon_days,
        price_basis="ADJUSTED",
        run_type=run_type,
        train_start_date=train_start,
        train_end_date=train_end,
        data_hash=f"{symbol}:{train_start}:{train_end}",
        status="SUCCESS",
    )

    db.add(run)
    db.flush()  # get run.id

    for row in results:

        target_date = row["date"]
        db.add(
            ForecastPoint(
                forecast_run_id=run.id,
                forecast_date=target_date,
                predicted_price=row["yhat"],
            )
        )

        if row.get("yhat_lower") is not None:
            db.add(
                ForecastInterval(
                    forecast_run_id=run.id,
                    forecast_date=target_date,
                    lower_bound=row["yhat_lower"],
                    upper_bound=row["yhat_upper"],
                    confidence_level=0.95,
                )
            )

    db.commit()
    cleanup_old_runs(db, run)


def cleanup_old_runs(db: Session, run: ForecastRun):
    old_ids = (
        db.query(ForecastRun.id)
        .filter(
            ForecastRun.symbol == run.symbol,
            ForecastRun.model_name == run.model_name,
            ForecastRun.model_version == run.model_version,
            ForecastRun.horizon_days == run.horizon_days,
            ForecastRun.status == "SUCCESS",
        )
        .order_by(ForecastRun.created_at.desc())
        .offset(FORECAST_RUN_RETENTION)
        .all()
    )

    if old_ids:
        db.query(ForecastRun).filter(
            ForecastRun.id.in_([r.id for r in old_ids])
        ).delete(synchronize_session=False)
        db.commit()

def get_forecast_for_target_date(
    db: Session,
    *,
    symbol: str,
    model_name: str,
    target_date: date,
):
    return (
        db.query(ForecastPoint, ForecastRun)
        .join(ForecastRun, ForecastPoint.forecast_run_id == ForecastRun.id)
        .filter(
            ForecastRun.symbol == symbol,
            ForecastRun.model_name == model_name,
            ForecastPoint.forecast_date == target_date,
            ForecastRun.status == "SUCCESS",
        )
        .all()
    )