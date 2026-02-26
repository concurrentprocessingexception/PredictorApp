from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from app.database import Base

class ForecastPoint(Base):
    __tablename__ = "forecast_points"

    id = Column(Integer, primary_key=True)
    forecast_run_id = Column(Integer, ForeignKey("forecast_runs.id", ondelete="CASCADE"), index=True)

    """The date for which the forecast is made."""
    forecast_date = Column(Date, nullable=False)
    """The predicted price for the forecast_date."""
    predicted_price = Column(Float, nullable=False)