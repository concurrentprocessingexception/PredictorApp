from sqlalchemy import Column, Integer, Float, Date, ForeignKey, Boolean, String
from app.database import Base

class ForecastError(Base):
    __tablename__ = "forecast_errors"

    id = Column(Integer, primary_key=True)

    forecast_point_id = Column(
        Integer,
        ForeignKey("forecast_points.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    symbol = Column(String(20), nullable=False, index=True)
    model_name = Column(String(50), nullable=False)
    horizon_days = Column(Integer, nullable=False)

    target_date = Column(Date, nullable=False)
    actual_price = Column(Float, nullable=False)
    predicted_price = Column(Float, nullable=False)

    error = Column(Float, nullable=False)        # actual - predicted
    abs_error = Column(Float, nullable=False)
    pct_error = Column(Float, nullable=True)

    within_interval = Column(Boolean, nullable=True)