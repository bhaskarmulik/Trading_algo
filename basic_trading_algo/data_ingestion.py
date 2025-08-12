# algotrade/data_ingestion.py
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
from .utils import logger
# import time

def __format(df: pd.DataFrame, symbol: str) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.rename(columns=str.upper)
    df.index = pd.to_datetime(df.index)
    df["SYMBOL"] = symbol
    return df.reset_index().rename(columns={"index": "DATETIME"})

def fetch_history(symbol: str, interval: str = "1d", months: int = 6) -> pd.DataFrame | None:
    end = datetime.now()
    start = end - timedelta(days=30*months + 10)
    logger.info(f"Fetching {interval} data for {symbol} from {start.date()} to {end.date()}")

    # 1) First try download() (simple, fast)
    try:
        df = yf.download(
            symbol, start=start, end=end, interval=interval,
            auto_adjust=False, progress=False, threads=False, timeout=45
        )
        if df is not None and len(df) > 0:  # Better check for data
            logger.info(f"Successfully fetched {len(df)} rows for {symbol} via download()")
            return __format(df, symbol)
        logger.warning(f"download() returned empty DataFrame for {symbol}")
    except Exception as e:
        logger.warning(f"yf.download failed for {symbol}: {e}")
        return pd.DataFrame()  # Return empty DataFrame on failure

    return pd.DataFrame()  # Return empty DataFrame if we get here