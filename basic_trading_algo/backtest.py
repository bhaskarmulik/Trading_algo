import pandas as pd
from dataclasses import dataclass
from typing import List

@dataclass
class Trade:
    symbol: str
    entry_date: pd.Timestamp
    entry_price: float
    exit_date: pd.Timestamp
    exit_price: float
    pnl_pct: float

def _flatten_cols(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    flat = []
    for c in out.columns:
        if isinstance(c, tuple):
            parts = [str(p) for p in c if str(p).strip() != ""]
            name = "_".join(parts) if parts else ""
        else:
            name = str(c)
        flat.append(name.strip("_"))  # strip trailing underscores from empty level
    out.columns = flat
    return out

def _pick_close_col(cols: List[str], symbol: str) -> str:
    cand = f"CLOSE_{symbol}"
    if cand in cols:
        return cand
    for c in cols:
        if c.startswith("CLOSE_"):
            return c
    if "CLOSE" in cols:
        return "CLOSE"
    ac1 = f"ADJ CLOSE_{symbol}"
    if ac1 in cols:
        return ac1
    if "ADJ_CLOSE" in cols:
        return "ADJ_CLOSE"
    if "ADJ CLOSE" in cols:
        return "ADJ CLOSE"
    #Incase none close-like feats are found
    raise KeyError(f"No CLOSE-like column found.")

def _pick_dt_col(cols: List[str]) -> str:
    # handle DATETIME or DATETIME_
    if "DATETIME" in cols:
        return "DATETIME"
    for c in cols:
        if c.startswith("DATETIME"):
            return c
    raise KeyError(f"No DATETIME-like column found. Available: {cols[:20]} ... (total {len(cols)})")

def backtest_long_only(df: pd.DataFrame):
    trades = []

    for sym, sdf in df.groupby("SYMBOL"):
        sdf = _flatten_cols(sdf.sort_values("DATETIME" if "DATETIME" in df.columns else df.columns[0]).copy())

        buy_cols = [c for c in sdf.columns if c.startswith("BUY_SIGNAL")]
        sdf["__BUY"] = sdf[buy_cols].astype(bool).any(axis=1) if buy_cols else False

        close_col = _pick_close_col(list(sdf.columns), str(sym))
        dt_col = _pick_dt_col(list(sdf.columns))

        # Process each buy signal
        for idx, row in sdf.iterrows():
            buy_signal = bool(row["__BUY"])
            
            if buy_signal:
                entry_date = pd.to_datetime(row[dt_col])
                entry_price = float(row[close_col])
                
                # Mark-to-market immediately with latest price
                exit_price = float(sdf.iloc[-1][close_col])
                exit_date = pd.to_datetime(sdf.iloc[-1][dt_col])
                pnl_pct = (exit_price - entry_price) / entry_price * 100.0
                trades.append(Trade(str(sym), entry_date, entry_price, exit_date, exit_price, pnl_pct))

    #Save the trades summary
    trades_df = pd.DataFrame([t.__dict__ for t in trades])
    if trades_df.empty:
        summary = pd.DataFrame([{"trades": 0, "wins": 0, "win_ratio": 0.0, "avg_pnl_pct": 0.0, "total_pnl_pct": 0.0}])
    else:
        wins = (trades_df["pnl_pct"] > 0).sum()
        summary = pd.DataFrame([{
            "trades": len(trades_df),
            "wins": wins,
            "win_ratio": wins / len(trades_df),
            "avg_pnl_pct": trades_df["pnl_pct"].mean(),
            "total_pnl_pct": trades_df["pnl_pct"].sum(),
        }])
    return trades_df, summary
