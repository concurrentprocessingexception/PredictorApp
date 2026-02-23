from sqlalchemy import Column, Integer, Float, Date, String, ForeignKey
from app.database import Base

class ForecastScenario(Base):
    __tablename__ = "forecast_scenarios"

    id = Column(Integer, primary_key=True)
    forecast_run_id = Column(Integer, ForeignKey("forecast_runs.id", ondelete="CASCADE"), index=True)

    forecast_date = Column(Date, nullable=False)
    scenario = Column(String, nullable=False)  # BULL | BASE | BEAR
    predicted_price = Column(Float, nullable=False)