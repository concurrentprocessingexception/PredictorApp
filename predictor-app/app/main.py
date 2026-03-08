from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from app.routers.news import get_company_news
from app.routers.upload import router as upload_router
from app.routers.history import router as history_router
from app.routers.forecast import router as forecast_router
from app.routers.forecasting import router as forecasting_router
from app.routers.reconciliation import router as reconciliation_router
from app.routers.forecast_metrics import router as forecast_metrics_router
from app.routers.model_comparison import router as model_comparison_router
from app.routers.stock import router as stock_router
from app.routers.news import router as news_router

import yfinance as yf
import os
from app.settings import settings


app = FastAPI()

# CORS setup using configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# register routers
app.include_router(history_router)
app.include_router(forecast_router)
app.include_router(reconciliation_router)
app.include_router(forecast_metrics_router)
app.include_router(model_comparison_router)
app.include_router(forecasting_router)
app.include_router(stock_router)
app.include_router(news_router)

# conditional upload route
if settings.upload_enabled:
    app.include_router(upload_router)
