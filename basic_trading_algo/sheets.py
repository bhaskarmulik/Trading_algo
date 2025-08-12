import os
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from .utils import logger

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def _get_client():
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path or not os.path.exists(creds_path):
        raise FileNotFoundError("Set GOOGLE_APPLICATION_CREDENTIALS to your service account JSON path")
    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    return gspread.auth.authorize(creds)

def write_tabs(sheet_name: str, trade_log: pd.DataFrame, summary: pd.DataFrame, ml_report: pd.DataFrame | None = None):
    gc = _get_client()
    try:
        sh = gc.open(sheet_name)
    except gspread.exceptions.SpreadsheetNotFound:
        logger.info(f"Creating sheet {sheet_name}")
        sh = gc.create(sheet_name)

    def upsert_worksheet(name: str, df: pd.DataFrame):
        try:
            ws = sh.worksheet(name)
            sh.del_worksheet(ws)
        except gspread.exceptions.WorksheetNotFound:
            pass
        ws = sh.add_worksheet(title=name, rows=max(len(df)+10, 100), cols=max(len(df.columns)+5, 20))
        if df.empty:
            df = pd.DataFrame({"Info": ["No data"]})
        header = [str(c) for c in df.columns]
        ws.update([header] + df.astype(str).values.tolist())

    upsert_worksheet("TradeLog", trade_log)
    upsert_worksheet("Summary", summary)
    if ml_report is not None:
        upsert_worksheet("MLReport", ml_report)
