from fastapi import APIRouter, HTTPException, Query
import yfinance as yf


router = APIRouter(prefix="/stock", tags=["Stock"])

@router.get("/{symbol}")
def get_stock_price(
    symbol: str,
    range: str = Query("1w", enum=["1d", "1w", "1m", "6m", "1y"])
):
    """
    Return historical close prices pulled from yfinance.
    """
    
    try:
        period_map = {
            "1d": ("1d", "5m"),
            "1w": ("5d", "15m"),
            "1m": ("1mo", "60m"),
            "6m": ("6mo", "1d"),
            "1y": ("1y", "1d"),
        }

        yf_period, interval = period_map.get(range, ("1d", "5m"))

        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=yf_period, interval=interval)

        if hist.empty:
            raise HTTPException(status_code=404, detail="No data found for given range")

        result = [
            {"date": i.strftime("%Y-%m-%d %H:%M"), "close": round(c, 2)}
            for i, c in zip(hist.index, hist["Close"])
        ]

        return {
            "symbol": symbol.upper(),
            "range": range,
            "data": result,
        }
    except HTTPException:
        # propagate existing HTTPExceptions unchanged
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
