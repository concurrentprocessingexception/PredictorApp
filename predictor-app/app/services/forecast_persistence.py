from app.models.forecast_run import ForecastRun
from app.models.forecast_point import ForecastPoint

FORECAST_RUN_RETENTION = 20

def save_forecast_run(db, run: ForecastRun, points, intervals, scenarios):
    db.add(run)
    db.flush()  # get run.id

    # insert points / intervals / scenarios
    # ...

    cleanup_old_runs(db, run)

def cleanup_old_runs(db, run):
    old_runs = (
        db.query(ForecastRun.id)
        .filter(
            ForecastRun.symbol == run.symbol,
            ForecastRun.model_name == run.model_name,
            ForecastRun.model_version == run.model_version,
            ForecastRun.horizon_days == run.horizon_days,
            ForecastRun.price_basis == run.price_basis,
            ForecastRun.status == "SUCCESS",
        )
        .order_by(ForecastRun.created_at.desc())
        .offset(FORECAST_RUN_RETENTION)
        .all()
    )

    if old_runs:
        ids = [r.id for r in old_runs]
        db.query(ForecastRun).filter(ForecastRun.id.in_(ids)).delete(
            synchronize_session=False
        )