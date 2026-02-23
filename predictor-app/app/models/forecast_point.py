from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from app.database import Base

class ForecastPoint(Base):
    __tablename__ = "forecast_points"

    id = Column(Integer, primary_key=True)
    forecast_run_id = Column(Integer, ForeignKey("forecast_runs.id", ondelete="CASCADE"), index=True)

    forecast_date = Column(Date, nullable=False)
    predicted_price = Column(Float, nullable=False)