from sqlalchemy import Column, Integer, String, Date, DateTime
from datetime import datetime
from app.database import Base

class ForecastRun(Base):
    __tablename__ = "forecast_runs"

    id = Column(Integer, primary_key=True)

    symbol = Column(String, index=True, nullable=False)

    model_name = Column(String, nullable=False)
    model_version = Column(String, nullable=False)

    horizon_days = Column(Integer, nullable=False)
    price_basis = Column(String, nullable=False)  # RAW | ADJUSTED
    run_type = Column(String, nullable=False)     # AUTO | MANUAL

    train_start_date = Column(Date, nullable=False)
    train_end_date = Column(Date, nullable=False)

    data_hash = Column(String, nullable=False)

    status = Column(String, nullable=False)       # SUCCESS | FAILED
    error_message = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)