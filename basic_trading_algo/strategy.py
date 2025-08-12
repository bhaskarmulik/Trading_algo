import pandas as pd
import numpy as np


# Functions to calculate metrics
def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff().astype(float)
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / (loss.replace(0, np.nan))
    rsi = 100 - (100 / (1 + rs))
    return rsi.bfill()


def moving_average(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window, min_periods=1).mean()

# Functions to calculate features
def compute_indicators(
    df: pd.DataFrame, rsi_period: int, short_dma: int = 20, long_dma: int = 50
) -> pd.DataFrame:
    out = df.copy()

    out["RSI"] = rsi(out["CLOSE"], period=rsi_period)
    out["DMA_S"] = moving_average(out["CLOSE"], window=short_dma)
    out["DMA_L"] = moving_average(out["CLOSE"], window=long_dma)

    out["DMA_CROSS_UP"] = (out["DMA_S"] > out["DMA_L"]) & (
        out["DMA_S"].shift(1) <= out["DMA_L"].shift(1)
    )

    return out


def generate_signals(df: pd.DataFrame, rsi_buy_th: int = 30) -> pd.DataFrame:
    out = df.copy()
    # Buy signal when RSI < 30 and 20DMA crosses up above 50DMA
    out["BUY_SIGNAL"] = (out["RSI"] < rsi_buy_th) & (out["DMA_CROSS_UP"])
    return out
