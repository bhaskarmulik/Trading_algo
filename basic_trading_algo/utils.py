from dataclasses import dataclass
from typing import List, Optional
import yaml
from dotenv import load_dotenv
import os
import asyncio
from telegram import Bot
from loguru import logger
import sys

#### Enable Logging functionality because errors acche hai  ####
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{message}</cyan>")
###### Data classes to store configs ######


@dataclass
class DataConfig:
    symbols: List[str]
    interval: str
    lookback_months: int
    backtest_months: int


@dataclass
class StrategyConfig:
    rsi_period: int
    short_dma: int
    long_dma: int
    rsi_buy_threshold: int


@dataclass
class MLConfig:
    enabled: bool
    features: List[str]
    model_type: str
    random_state: int


@dataclass
class SheetsConfig:
    enabled: bool
    sheet_name_env: str


@dataclass
class AlertsConfig:
    enabled: bool


@dataclass
class RunnerConfig:
    schedule_cron: Optional[str]


@dataclass
class Config:
    data: DataConfig
    strategy: StrategyConfig
    ml: MLConfig
    sheets: SheetsConfig
    alerts: AlertsConfig
    runner: RunnerConfig


################################################   HELPER FUNCTIONS HERE #########################################


# Telegram Bot alerting stuff


async def _send_async(token, chat_id, message):
    if Bot is None:
        raise RuntimeError("python-telegram-bot not installed")
    bot = Bot(token=token)
    await bot.send_message(chat_id=chat_id, text=message)


def send_telegram(message: str) -> Optional[str]:
    if Bot is None:
        logger.warning("python-telegram-bot not installed")
        return None
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        logger.info("Telegram not configured")
        return None
    try:
        asyncio.run(_send_async(token, chat_id, message))
        return "sent"
    except Exception as e:
        logger.error(f"Telegram send failed: {e}")
        return None


# Loading config


def load_config(path: str = "configs/config.yaml") -> Config:
    load_dotenv()
    with open(path, "r") as f:
        raw = yaml.safe_load(f)

    return Config(
        data=DataConfig(**raw["data"]),
        strategy=StrategyConfig(**raw["strategy"]),
        ml=MLConfig(**raw["ml"]),
        sheets=SheetsConfig(**raw["sheets"]),
        alerts=AlertsConfig(**raw["alerts"]),
        runner=RunnerConfig(**raw["runner"]),
    )
