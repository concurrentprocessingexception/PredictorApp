from fastapi import HTTPException
import yfinance as yf


def get_stock_price_data(symbol: str, range: str):
    """Return historical close prices pulled from yfinance.

    This helper is kept separate from the FastAPI route so that the
    endpoint itself can remain small and easily tested, just like the
    /news handler.
    """
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
