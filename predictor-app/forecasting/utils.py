# Data transformations & helpers

import pandas as pd

def to_prophet_dataframe(rows):
    """
    Converts DB rows into Prophet-compatible DataFrame.
    Prophet expects:
      ds -> datetime
      y  -> target value
    """
    df = pd.DataFrame(rows, columns=["ds", "y"])
    return df
