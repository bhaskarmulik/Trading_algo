# MiniAlgo Trading System

A Python-based algorithmic trading system that implements technical analysis, backtesting, and machine learning for stock market trading strategies.

## Features

- **Data Ingestion**: Fetches historical stock data
- **Technical Analysis**: 
  - RSI (Relative Strength Index)
  - DMA (Double Moving Average)
  - Short and Long term moving averages
  - DMA crossover signals

- **Trading Strategy**:
  - Long-only trading strategy
  - Buy signal generation based on technical indicators
  - Automatic trade entry point detection

- **Machine Learning**:
  - Predicts next-day price movements
  - Uses technical indicators as features:
    - RSI
    - Short-term DMA
    - Long-term DMA
    - DMA crossover signals
  - Supports multiple ML models:
    - Logistic Regression
    - Decision Tree Classifier

- **Backtesting**:
  - Performance analysis of trading strategies
  - Trade-by-trade analysis
  - Key performance metrics:
    - Number of trades
    - Win ratio
    - Average PnL%
    - Total PnL%

- **Reporting**:
  - Generates detailed trade logs
  - Signal analysis reports
  - ML model performance reports
  - Optional Google Sheets integration
  - Telegram alerts support

## Project Structure

```
├── algotrade/
│   ├── __init__.py
│   ├── backtest.py      # Backtesting engine
│   ├── data_ingestion.py # Data fetching and processing
│   ├── main.py          # Main pipeline execution
│   ├── ml.py            # Machine learning models
│   ├── sheets.py        # Google Sheets integration
│   ├── strategy.py      # Trading strategy implementation
│   └── utils.py         # Utility functions
├── configs/
│   └── config.yaml      # Configuration settings
├── logs/                # Log files
└── reports/             # Generated reports
    ├── ml_report.csv
    ├── signal_counts_by_symbol.csv
    ├── signals_triggered.csv
    ├── summary.csv
    └── trade_log.csv
```

## Configuration

Configure the system through `configs/config.yaml`. Key settings include:

- Data parameters (symbols, interval, lookback period)
- Strategy parameters (RSI period, DMA periods)
- ML parameters (features, model type, test size)
- Reporting options (Google Sheets, Telegram alerts)

## Usage

1. Set up configuration in `config.yaml`
2. Run the main pipeline:
```python
python -m algotrade.main
```

## Reports Generated

1. **trade_log.csv**: Detailed record of all trades
2. **summary.csv**: Overall performance metrics
3. **signals_triggered.csv**: Record of all triggered signals
4. **signal_counts_by_symbol.csv**: Signal frequency by symbol
5. **ml_report.csv**: Machine learning model performance

## Machine Learning

The system uses machine learning to predict price movements:
- Features: Technical indicators (RSI, DMA)
- Target: Next day's price movement (up/down)
- Models: Logistic Regression or Decision Trees
- Evaluation: Accuracy scoring on time-series split

## Dependencies

- pandas: Data manipulation
- scikit-learn: Machine learning
- Technical analysis libraries
- Google Sheets API (optional)
- Telegram API (optional)

## Notes

- The system is designed for long-only strategies
- All trades are marked to market at the end of the testing period
- Machine learning predictions are based on technical indicators
- Supports multiple stock symbols simultaneously

## Limitations

- Currently implements long-only strategies
- No risk management features
- No position sizing logic
- Assumes end-of-day trading
