import numpy as np
import pandas as pd

def to_prophet_dataframe(rows):
    """
    Converts DB rows into Prophet-compatible DataFrame.
    Prophet expects:
      ds -> datetime
      y  -> target value
    """
    df = pd.DataFrame(rows, columns=["ds", "y"])
    df["y"] = np.log(df["y"])  # Log-transform for better forecasting stability
    return df
