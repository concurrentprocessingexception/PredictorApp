from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from app.database import Base

class ForecastInterval(Base):
    __tablename__ = "forecast_intervals"

    id = Column(Integer, primary_key=True)
    forecast_run_id = Column(Integer, ForeignKey("forecast_runs.id", ondelete="CASCADE"), index=True)

    forecast_date = Column(Date, nullable=False)
    lower_bound = Column(Float, nullable=False)
    upper_bound = Column(Float, nullable=False)
    confidence_level = Column(Float, nullable=False)