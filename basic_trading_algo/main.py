import pandas as pd
from .utils import load_config, logger, send_telegram
from .data_ingestion import fetch_history
from .strategy import compute_indicators, generate_signals
from .backtest import backtest_long_only
from .ml import train_simple_classifier 
from .sheets import write_tabs
import os

def run_pipeline():

    #Loading config from config.yaml
    cfg = load_config()

    frames = []
    for sym in cfg.data.symbols:
        df = fetch_history(sym, interval=cfg.data.interval, months=cfg.data.lookback_months)
        if df is None:
            logger.error(f"Didnt fetch the data for : {sym}")
            continue
        df = df.rename(columns={
            "Date": "DATETIME", "Open": "OPEN", "High": "HIGH",
            "Low": "LOW", "Close": "CLOSE", "Adj Close": "ADJ_CLOSE", "Volume": "VOLUME"
        })
        ind = compute_indicators(df, cfg.strategy.rsi_period, cfg.strategy.short_dma, cfg.strategy.long_dma)
        frames.append(ind)

    if not frames:
        logger.error("No data fetched.")
        return None

    full = pd.concat(frames, ignore_index=True).sort_values(["SYMBOL", "DATETIME"])
    sig = generate_signals(full, cfg.strategy.rsi_buy_threshold)

    # Backtest
    trades_df, summary_df = backtest_long_only(sig)

    ml_rows = []
    if cfg.ml.enabled:
        for sym, sdf in sig.groupby("SYMBOL"):
            try:

                clf, acc, idx, preds = train_simple_classifier(
                    sdf,
                    features=cfg.ml.features,
                    model_type=cfg.ml.model_type,
                    random_state=cfg.ml.random_state,
                    symbol=str(sym),
                )
                if clf is not None and acc is not None:
                    logger.info(f"ML for {sym}: accuracy={round(acc, 4)} (samples={len(idx) if idx is not None else 'n/a'})")
                    ml_rows.append({
                        "SYMBOL": sym,
                        "ACCURACY": round(acc, 4),
                        "SAMPLES": int(len(idx)) if idx is not None else 0
                    })
                else:
                    logger.warning(f"ML skipped for {sym} — insufficient samples or target variance")
            except Exception as e:
                logger.error(f"ML failed for {sym}: {e}")

    ml_report = pd.DataFrame(ml_rows) if ml_rows else None

    # Save locally
    trades_df.to_csv("reports/trade_log.csv", index=False)
    summary_df.to_csv("reports/summary.csv", index=False)
    if ml_report is not None:
        ml_report.to_csv("reports/ml_report.csv", index=False)

    # Google Sheets logic
    if cfg.sheets.enabled:
        try:
            sheet_name = os.getenv(cfg.sheets.sheet_name_env, "MiniAlgoTrade")
            write_tabs(sheet_name, trades_df, summary_df, ml_report)
            logger.info(f"Wrote to Google Sheets: {sheet_name}")
        except Exception as e:
            logger.error(f"Sheets write failed: {e}")
            send_telegram(f"Sheets write failed: {e}")

    # Telegram alert logic
    if cfg.alerts.enabled:
        try:
            msg = f"Run complete. Trades: {len(trades_df)} | Win%: {summary_df.iloc[0]['win_ratio']:.2%}"
            send_telegram(msg)
        except Exception as e:
            logger.error(f"Alert failed: {e}")

    return {"trades": trades_df, "summary": summary_df, "ml_report": ml_report}

if __name__ == "__main__":
    run_pipeline()